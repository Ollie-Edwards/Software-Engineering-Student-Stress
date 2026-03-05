import React, { useEffect, useState } from "react";

export default function Home({isAdding, setIsAdding}) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const uncompletedTasks = tasks.filter(task => !task.completed);
  const completedTasks = tasks.filter(task => task.completed);
  const [sortOrder, setSortOrder] = useState("desc");

    useEffect(() => {
    async function fetchTasks() {
      try {
        const res = await fetch("http://localhost:8000/tasks");
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        const data = await res.json();
        setTasks(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchTasks();
  }, []);

  if (loading) return <div className="p-4 text-lg">Loading tasks...</div>;
  if (error) return <div className="p-4 text-red-500">Error: {error}</div>;

  /*ADDED*/

  const handleCreateTask = async (e) => {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);

    const payload = {
      title: formData.get("title"),
      description: formData.get("description"),
      importance: Number(formData.get("importance")),
      length: Number(formData.get("length")),
      due_at: formData.get("due_at") ? new Date(formData.get("due_at")).toISOString() : null,
      // due_at: formData.get("due_at"),
    };

    const res = await fetch("http://localhost:8000/tasks", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const newTask = await res.json();

    setTasks((prev) => [...prev, newTask]);
    setIsAdding(false);
  };

  /*ADDED*/

  const Taskcard = (task) => {
    {/* High (8-10), Medium (4-7), Low (1-3)*/}
          const isHigh = task.importance >= 8;
          const isMedium = task.importance >= 4 && task.importance < 8;

          const barColor = isHigh ? 'bg-red-500' : isMedium ? 'bg-amber-400' : 'bg-emerald-500';
          const badgeBg = isHigh ? 'bg-red-100' : isMedium ? 'bg-amber-100' : 'bg-emerald-100';
          const badgeText = isHigh ? 'text-red-700' : isMedium ? 'text-amber-700' : 'text-emerald-700';
          const priorityLabel = isHigh ? 'High' : isMedium ? 'Medium' : 'Low';

          const toggleReminder = (e) => {e.stopPropagation(); setTasks(prevTasks => prevTasks.map(t => t.id === task.id ? { ...t, reminder: !t.reminder } : t));};

          return(
          <div key={task.id} onClick={() => setEditingTask(task)} className="cursor-pointer relative flex border rounded-2xl shadow-sm overflow-hidden bg-white">
            <div className={`w-2 shrink-0 ${barColor}`} />
            <div className="p-5 flex-1 flex flex-col gap-3">
              {/* Title */}
              <div className ="flex justify-between items-start">
                <div>
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase mb-1 inline-block ${badgeBg} ${badgeText}`}>
                    • {priorityLabel} ({task.importance})
                  </span>
                  <h2 className="text-xl font-bold text-slate-800 leading-tight">{task.title}</h2>
                </div>
                <div className="flex items-center gap-1">
                <button onClick={toggleReminder} className={`p-2 transition-all rounded-lg ${task.reminder ? 'text-indigo-600' : 'text-slate-400'}`}>
                  {task.reminder ? (
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="h-5 w-5 text-slate-400">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" />
                    </svg>
                  ) : (
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M3 3l18 18M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" />
                    </svg>
                  )}
                </button>
                <button onClick={(e) => e.stopPropagation()} className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors rounded-lg" title="Delete Task">
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>  
                </div>
              </div>

              {/* Description */}
              <p className="text-slate-600 text-sm line-clamp-2">{task.description}</p>

              {/* Detail info */}
              <div className="grid grid-cols-2 gap-y-2 gap-x-4 pt-4 border-t mt-auto text-xs text-slate-500">
                <p><strong>Status:</strong> {task.completed ? "Completed" : "Not Completed"}</p>
                <p><strong>Importance:</strong> {task.importance}</p>
                <p><strong>Length:</strong> {task.length}</p>
                <p><strong>Due At:</strong> {task.due_at ? new Date(task.due_at).toLocaleString() : "N/A"}</p>
                <p><strong>Created At:</strong> {task.created_at ? new Date(task.created_at).toLocaleString() : "N/A"}</p>
                <p><strong>Updated At:</strong> {task.updated_at ? new Date(task.updated_at).toLocaleString() : "N/A"}</p>
                {/*<p><strong>Created At:</strong> {new Date(task.created_at).toLocaleString()}</p>
                <p><strong>Updated At:</strong> {new Date(task.updated_at).toLocaleString()}</p>
                  */}
              </div>
          </div>
          </div>
          )
  }

  return (
    <div className="p-6 space-y-4">
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Tasks</h1>
          <p className="text-slate-500 mt-1">
            You have{" "}
            <span className="font-semibold text-indigo-600">
              {uncompletedTasks.length}
            </span>{" "}
            tasks remaining.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-white border px-3 py-1.5 rounded-lg shadow-sm">
          <span className="text-xs font-bold text-slate-400 uppercase">
            Sort By
          </span>
          <select
            className="text-xs text-slate-600 font-semibold bg-transparent focus:outline-none cursor-pointer"
            value={sortOrder}
            onChange={(e) => setSortOrder(e.target.value)}
          >
            <option value="desc">Highest to Lowest priority</option>
            <option value="asc">Lowest to Highest priority</option>
          </select>
        </div>
      </div>

      {uncompletedTasks.length === 0 && <p>No tasks found.</p>}
      <div className="grid gap-4">
        {[...uncompletedTasks]
          .sort((a, b) => {
            return sortOrder === "desc"
              ? b.importance - a.importance
              : a.importance - b.importance;
          })
          .map((task) => Taskcard(task))}
      </div>

      {completedTasks.length > 0 && (
        <div className="mt-12 space-y-4 pt-8 border-t border-dashed">
          <h1 className="text-3xl font-bold text-slate-900">Completed</h1>
          <p className="text-slate-500 mt-1">
            You have completed{" "}
            <span className="font-semibold text-indigo-600">
              {completedTasks.length}
            </span>{" "}
            tasks.
          </p>
          <div className="grid gap-4">
            {[...completedTasks]
              .sort((a, b) => {
                return sortOrder === "desc"
                  ? b.importance - a.importance
                  : a.importance - b.importance;
              })
              .map((task) => Taskcard(task))}
          </div>
        </div>
      )}

      {editingTask && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden">
            <div className="p-6 border-b flex justify-between items-center">
              <h2 className="text-xl font-bold text-slate-800">Edit Task</h2>
              <button
                onClick={() => setEditingTask(null)}
                className="text-slate-400 hover:text-slate-600 text-2xl"
              >
                &times;
              </button>
            </div>

            <form onSubmit={handleCreateTask} className="p-6 space-y-4">
              {/* <form className="p-6 space-y-4"> */}
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase mb-1">
                  Title
                </label>
                <input
                  required
                  className="w-full border rounded-xl px-4 py-2 focus:ring-2 focus:ring-indigo-500 outline-none"
                  defaultValue={editingTask.title}
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase mb-1">
                  Description
                </label>
                <textarea
                  className="w-full border rounded-xl px-4 py-2 h-32 focus:ring-2 focus:ring-indigo-500 outline-none"
                  defaultValue={editingTask.description}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">
                    Importance (1-10)
                  </label>
                  <input
                    name="importance"
                    type="number"
                    min="1"
                    max="10"
                    defaultValue={editingTask.importance}
                    className="w-full border rounded-xl px-4 py-2 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">
                    Length (e.g. 30m)
                  </label>
                  <input
                    name="length"
                    defaultValue={editingTask.length}
                    className="w-full border rounded-xl px-4 py-2 outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">
                  Due Date
                </label>
                <input
                  name="due_at"
                  type="datetime-local"
                  defaultValue={
                    editingTask.due_at
                      ? editingTask.due_at.substring(0, 16)
                      : ""
                  }
                  className="w-full border rounded-xl px-4 py-2 outline-none"
                />
              </div>

              <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
                <input
                  name="completed"
                  type="checkbox"
                  defaultChecked={editingTask.completed}
                  className="w-5 h-5 accent-indigo-600"
                />
                <span className="text-sm font-semibold text-slate-700">
                  Mark as Completed
                </span>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setEditingTask(null)}
                  className="flex-1 px-4 py-3 rounded-xl font-bold text-slate-500 bg-slate-100 hover:bg-slate-200 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-3 rounded-xl font-bold text-white bg-indigo-600 hover:bg-indigo-700 shadow-lg shadow-indigo-200 transition-all"
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {isAdding && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden">
            <div className="p-6 border-b flex justify-between items-center bg-indigo-50">
              <h2 className="text-xl font-bold text-slate-800">
                Create New Task
              </h2>
              <button
                onClick={() => setIsAdding(false)}
                className="text-slate-400 hover:text-slate-600 text-2xl"
              >
                &times;
              </button>
            </div>

            <form onSubmit={handleCreateTask} className="p-6 space-y-4">
              {/* <form className="p-6 space-y-4"> */}
              <div>
                <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">
                  Title
                </label>
                <input
                  name="title"
                  required
                  placeholder="Title"
                  className="w-full border rounded-xl px-4 py-2 outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">
                  Description
                </label>
                <textarea
                  name="description"
                  placeholder="Add some details..."
                  className="w-full border rounded-xl px-4 py-2 h-20 outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">
                  Due Date & Time
                </label>
                <input
                  name="due_at"
                  type="datetime-local"
                  className="w-full border rounded-xl px-4 py-2 outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">
                    Importance (1-10)
                  </label>
                  <input
                    name="importance"
                    required
                    type="number"
                    min="1"
                    max="10"
                    placeholder="5"
                    className="w-full border rounded-xl px-4 py-2 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">
                    Length
                  </label>
                  <input
                    name="length"
                    type="number"
                    min="0"
                    placeholder="30"
                    className="w-full border rounded-xl px-4 py-2 outline-none"
                  />
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setIsAdding(false)}
                  className="flex-1 px-4 py-3 rounded-xl font-bold text-slate-500 bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-3 rounded-xl font-bold text-white bg-indigo-600 shadow-lg shadow-indigo-200"
                >
                  Create Task
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
