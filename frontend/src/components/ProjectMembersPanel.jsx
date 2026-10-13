// src/components/ProjectMembersPanel.jsx
import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import { searchUsersToAdd } from "../api/projectMemberApi";
import { getErrorMessage } from "../utils/apiError";
import useDebounce from "../hooks/useDebounce";
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

  // Ô tìm kiếm user: state cục bộ vì chỉ panel này dùng
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);      // null = chưa tìm, [] = không có kết quả
  const [searching, setSearching] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);

  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState("");

  // Tải thành viên của project
  useEffect(() => {
    const promise = dispatch(fetchMembers(projectId));
    return () => promise.abort();
  }, [dispatch, projectId]);

  // Tìm user theo từ khóa đã debounce 500ms, hủy request cũ khi từ khóa đổi
  const debouncedQuery = useDebounce(query.trim(), 500);
  const loading = searching || query.trim() !== debouncedQuery; // đang chờ hết delay hoặc đang gọi API

  useEffect(() => {
    if (!debouncedQuery) {
      setResults(null);
      setSearching(false);
      return;
    }

    const controller = new AbortController();
    setSearching(true);
    searchUsersToAdd(projectId, debouncedQuery, controller.signal)
      .then((data) => {
        setResults(data);
        setSearching(false);
      })
      .catch((err) => {
        if (err.code === "ERR_CANCELED" || err.name === "CanceledError") return;
        setActionError(getErrorMessage(err));
        setSearching(false);
      });

    return () => controller.abort();
  }, [debouncedQuery, projectId]);

  function handlePick(user) {
    setSelectedUser(user);
    setQuery("");
    setResults(null);
    setActionError("");
  }

  async function handleAdd() {
    if (!selectedUser) return;
    setBusy(true);
    setActionError("");
    try {
      await dispatch(addMember({ projectId, userId: selectedUser.id })).unwrap();
      setSelectedUser(null);
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
        {selectedUser ? (
          <div className="members-selected">
            <span>
              {selectedUser.full_name} <small>{selectedUser.email}</small>
            </span>
            <button
              type="button"
              onClick={() => setSelectedUser(null)}
              disabled={busy}
              title="Chọn người khác"
            >
              ×
            </button>
          </div>
        ) : (
          <div className="members-search">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Tìm theo tên hoặc email..."
              disabled={busy}
              autoComplete="off"
            />

            {query.trim() && (
              <ul className="members-search-results">
                {loading && <li className="state-message">Đang tìm...</li>}
                {!loading && results && results.length === 0 && (
                  <li className="state-message">Không tìm thấy người phù hợp.</li>
                )}
                {!loading && results && results.map((u) => (
                  <li key={u.id}>
                    <button type="button" onClick={() => handlePick(u)}>
                      {u.full_name} <small>{u.email}</small>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        <button type="button" onClick={handleAdd} disabled={busy || !selectedUser}>
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
