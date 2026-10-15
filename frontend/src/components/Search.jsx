export default function TaskSearch({ value, onChange,placeholder = "Search...", }) {
  return (
    <div className="task-search">

      <span className="search-icon">
        ⌕
      </span>

      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
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