// src/components/ProjectMembersPanel.jsx
import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import { getUsers } from "../api/userApi";
import { getErrorMessage } from "../utils/apiError";
import { fetchMembers, addMember, removeMember } from "../features/projectMembers/projectMembersSlice";
import {
  selectMembers, selectMembersStatus, selectMembersError,
} from "../features/projectMembers/projectMembersSelectors";

export default function ProjectMembersPanel({ project, onClose }) {
  const dispatch = useDispatch();
  const projectId = project.id;

  const members = useSelector((s) => selectMembers(s, projectId));
  const status = useSelector((s) => selectMembersStatus(s, projectId));
  const error = useSelector((s) => selectMembersError(s, projectId));

  const [users, setUsers] = useState([]);       // chỉ panel này dùng nên để state cục bộ
  const [selectedUserId, setSelectedUserId] = useState("");
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState("");

  // Tải thành viên của project
  useEffect(() => {
    const promise = dispatch(fetchMembers(projectId));
    return () => promise.abort();
  }, [dispatch, projectId]);

  // Tải danh sách user để chọn
  useEffect(() => {
    const controller = new AbortController();
    getUsers({}, controller.signal)
      .then((data) => setUsers(Array.isArray(data) ? data : data.items ?? []))
      .catch((err) => {
        if (err.code !== "ERR_CANCELED") setActionError(getErrorMessage(err));
      });
    return () => controller.abort();
  }, []);

  const memberIds = new Set(members.map((m) => m.user_id));
  const availableUsers = users.filter((u) => !memberIds.has(u.id));

  async function handleAdd() {
    if (!selectedUserId) return;
    setBusy(true);
    setActionError("");
    try {
      await dispatch(addMember({ projectId, userId: selectedUserId })).unwrap();
      setSelectedUserId("");
    } catch (err) {
      setActionError(typeof err === "string" ? err : err.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleRemove(member) {
    if (!window.confirm(`Gỡ ${member.user.full_name} khỏi project?`)) return;
    setBusy(true);
    setActionError("");
    try {
      await dispatch(removeMember({ projectId, userId: member.user_id })).unwrap();
    } catch (err) {
      setActionError(typeof err === "string" ? err : err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="members-panel">
      <div className="drawer-header">
        <h2>Thành viên: {project.name}</h2>
        <button type="button" className="drawer-close" onClick={onClose}>×</button>
      </div>

      {/* Thêm thành viên */}
      <div className="members-add">
        <select
          value={selectedUserId}
          onChange={(e) => setSelectedUserId(e.target.value)}
          disabled={busy}
        >
          <option value="">Chọn người để thêm...</option>
          {availableUsers.map((u) => (
            <option key={u.id} value={u.id}>{u.full_name} ({u.email})</option>
          ))}
        </select>
        <button type="button" onClick={handleAdd} disabled={busy || !selectedUserId}>
          Thêm
        </button>
      </div>

      {actionError && <div className="action-error">{actionError}</div>}

      {/* 4 trạng thái: loading, error, empty, success */}
      {status === "loading" && <div className="state-message">Đang tải thành viên...</div>}
      {status === "error" && <div className="state-message state-error">Không tải được: {error}</div>}
      {status === "success" && members.length === 0 && (
        <div className="state-message">Project chưa có thành viên.</div>
      )}

      {members.length > 0 && (
        <ul className="members-list">
          {members.map((m) => (
            <li key={m.user_id}>
              <span>
                {m.user.full_name} <small>{m.user.email}</small>
                {m.user_id === project.owner_id && <em> (chủ sở hữu)</em>}
              </span>
              <button
                type="button"
                onClick={() => handleRemove(m)}
                disabled={busy || m.user_id === project.owner_id}
                title={m.user_id === project.owner_id ? "Không thể gỡ chủ sở hữu" : "Gỡ khỏi project"}
              >
                Gỡ
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}