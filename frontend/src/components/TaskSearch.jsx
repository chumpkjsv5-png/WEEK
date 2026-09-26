export default function TaskSearch({ value, onChange }) {
  return (
    <div className="task-search">

      <span className="search-icon">
        ⌕
      </span>

      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Search tasks..."
      />

      {value && (
        <button
          type="button"
          className="clear-search"
          onClick={() => onChange("")}
        >
          ×
        </button>
      )}

    </div>
  );
}