export default function TaskTabs({ value, onChange }) {
  const tabs = [
    {
      label: "All",
      value: "",
    },
    {
      label: "Active",
      value: "pending",
    },
    {
      label: "Completed",
      value: "completed",
    },
  ];

 function handleChange(tab) {
  onChange(tab.value);
}

  return (
    <div className="task-tabs">

      {tabs.map((tab) => (
        <button
          key={tab.value}
          type="button"
          className={
            value === tab.value
              ? "active"
              : ""
          }
          onClick={() => handleChange(tab)}
        >
          {tab.label}
        </button>
      ))}

    </div>
  );
}