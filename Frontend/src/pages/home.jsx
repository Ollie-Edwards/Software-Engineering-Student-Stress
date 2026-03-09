import React, { useEffect, useState } from "react";
import LinkButton from '../components/linkElement';

export default function Home({isAdding, setIsAdding}) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const uncompletedTasks = tasks.filter(task => !task.completed);
  const completedTasks = tasks.filter(task => task.completed);
  const [sortOrder, setSortOrder] = useState("desc");
  const [showSubtasks, setShowSubtasks] = useState(false);

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

  const timeUntil = (dateStr) => {
    if (!dateStr) return "No due date";
    const diff = new Date(dateStr) - new Date();
    if (diff < 0) return "Overdue";

    const mins  = Math.floor(diff / 60000);
    const hours = Math.floor(mins / 60);
    const days  = Math.floor(hours / 24);
    const weeks = Math.floor(days / 7);

    if (weeks > 0)      return `${weeks}w ${days % 7}d`;
    if (days > 0)       return `${days}d ${hours % 24}h`;
    if (hours > 0)      return `${hours}h ${mins % 60}m`;
    if (mins > 0)       return `${mins}m`;
    return "Due now";
  };

  const Taskcard = (task) => {
      const priorityColor = (p) => {
        if (p <= 40)  return '#00cc00';
        if (p <= 60)  return '#d6da17';
        if (p <= 80)  return '#ff7300';
        return '#ff0000';
      };

      const priorityBadgeBg = (p) => {
        if (p <= 40)  return '#ccffcc';
        if (p <= 60)  return '#eeffcc';
        if (p <= 80)  return '#ffe5cc';
        return '#ffcccc';
      };

        const badgeBg      = priorityBadgeBg(task.priority);
        const badgeText    = '#000000'
        const priorityLabel = task.priority >= 80 ? 'High' : task.priority >= 40 ? 'Medium' : 'Low';

          const toggleReminder = (e) => {e.stopPropagation(); setTasks(prevTasks => prevTasks.map(t => t.id === task.id ? { ...t, reminder: !t.reminder } : t));};

          const toggleComplete = async (e) => {
                  e.stopPropagation();
                  const currentlyCompleted = task.completed; 
                  const newStatus = !currentlyCompleted;

                  setTasks(prevTasks => prevTasks.map(t => 
                    t.id === task.id ? { ...t, completed: newStatus } : t
                  ));
                  const endpoint = newStatus ? 'complete' : 'reopen';
                  const url = `http://localhost:8000/tasks/task/${task.id}/${endpoint}`;

                  try {
                    const response = await fetch(url, { method: 'POST' });

                    if (!response.ok) {
                      throw new Error("Database update failed");
                    }
                  } catch (error) {
                    console.error(error);
                    setTasks(prevTasks => prevTasks.map(t => 
                    t.id === task.id ? { ...t, completed: currentlyCompleted } : t
                    ));
                  }
            }

          const toggleSubtask = async (subtask) => {
          const endpoint = subtask.completed ? 'reopen' : 'complete';
          try {
            const response = await fetch(`http://localhost:8000/subtask/${subtask.id}/${endpoint}`, {
              method: 'POST',
            });
            if (response.ok) onRefresh(); // Refresh the list to see parent task auto-complete
          } catch (err) {
            console.error("Fetch error:", err);
          }
          };

          return(
          <div key={task.id} onClick={() => setEditingTask(task)} className="cursor-pointer relative flex border rounded-2xl shadow-sm overflow-hidden bg-white">
            <div style={{ backgroundColor: badgeBg, color: badgeText }} className={`w-2 shrink-0`} />
            <div className="p-5 flex-1 flex flex-col gap-3">
              {/* Title */}
              <div className ="flex justify-between items-start">
                <div>
                  <span style={{ backgroundColor: badgeBg, color: badgeText }} className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase mb-1 inline-block`}>
                    • {priorityLabel} ({task.priority})
                  </span>
                  <h2 className="text-xl font-bold text-slate-800 leading-tight">{task.title}</h2>
                </div>
                <div className="flex items-center gap-1">

                  {/* If available then render link */}
                  <LinkButton url={task.reference_url} />

                  <button onClick={toggleComplete} className="focus:outline-none transition-transform active:scale-90">
                  {task.completed ? (
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 text-slate-400 hover:text-black">
                      <rect x="3" y="3" width="18" height="18" rx="3" />
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75" />
                    </svg>
                  ) : (
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 text-slate-400 hover:text-black">
                      <rect x="3" y="3" width="18" height="18" rx="3" />
                    </svg>
                  )}
                </button>
                <button onClick={(e) => {e.stopPropagation(); handleDeleteTask(task.id);}} className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors rounded-lg" title="Delete Task">
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>  
                <button onClick={(e) => {e.stopPropagation(); setShowSubtasks(!showSubtasks);}} className="p-1 hover:bg-slate-100 rounded transition-colors">
                  <svg xmlns="http://www.w3.org/2000/svg" className={`h-5 w-5 transform transition-transform ${showSubtasks ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
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
                <p><strong>Due:</strong> {timeUntil(task.due_at)}</p>
              </div>
          </div>
          </div>
          )
  }

  const handleUpdateTask = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);

    const updatedData = {
      title: formData.get('title'),
      description: formData.get('description'),
      importance: parseInt(formData.get('importance')) || 0,
      length: parseInt(formData.get('length')) || null,
      reminder_enabled: formData.get('reminder') === 'on' 
    };

    try {
      const response = await fetch(`http://localhost:8000/tasks/${editingTask.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedData),
      });

      if (response.ok) {
        const savedTask = await response.json();
        setTasks(prev => prev.map(t => t.id === savedTask.id ? savedTask : t));
        setEditingTask(null);
      }
    } catch (error) {
      console.error("Update failed:", error);
    }
  };

  const handleCreateTask = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);

    const newTaskData = {
      user_id: 1,
      title: formData.get('title'),
      description: formData.get('description'),
      importance: parseInt(formData.get('importance')) || 0,
      length: parseInt(formData.get('length')) || null,
      due_at: formData.get('due_at') ? new Date(formData.get('due_at')).toISOString() : null,
      reminder_enabled: formData.get('reminder') === 'on',
      completed: false
    };

    try {
      const response = await fetch('http://localhost:8000/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTaskData),
      });

      if (response.ok) {
        const createdTask = await response.json();
        setTasks(prev => [...prev, createdTask]);
        setShowCreateModal(false);
      }
      } catch (error) {
      console.error("Task creation failed:", error);
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (!window.confirm("Are you sure you want to delete this task?")) return;
  
    try {
      const response = await fetch(`http://localhost:8000/tasks/${taskId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setTasks(prev => prev.filter(task => task.id !== taskId));
      
        if (editingTask?.id === taskId) {
          setEditingTask(null);
        }
      } else {
        console.error("Failed to delete task");
      }
    } catch (error) {
      console.error("Error during deletion:", error);
    }
  };

  return (
    <div className="p-6 space-y-4">
      <div className="flex justify-between items-end mb-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Tasks</h1>
        <p className="text-slate-500 mt-1">
          You have <span className="font-semibold text-indigo-600">{uncompletedTasks.length}</span> tasks remaining.
        </p>
      </div>

      <div className="flex items-center gap-2 bg-white border px-3 py-1.5 rounded-lg shadow-sm">
        <span className="text-xs font-bold text-slate-400 uppercase">Sort By</span>
        <select className="text-xs text-slate-600 font-semibold bg-transparent focus:outline-none cursor-pointer" value = {sortOrder} onChange={(e) => setSortOrder(e.target.value)}>
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
              ? b.priority - a.priority
              : a.priority - b.priority;
          })
          .map(task => Taskcard(task))}
      </div>  

      {completedTasks.length > 0 && (
        <div className="mt-12 space-y-4 pt-8 border-t border-dashed">
          <h1 className="text-3xl font-bold text-slate-900">Completed</h1>
          <p className="text-slate-500 mt-1">
            You have completed <span className="font-semibold text-indigo-600">{completedTasks.length}</span> tasks.
          </p>
          <div className="grid gap-4"> 
            {[...completedTasks]
              .sort((a, b) => {
                return sortOrder === "desc" 
                  ? b.importance - a.importance
                  : a.importance - b.importance;
              })
              .map(task => Taskcard(task))}
          </div>
        </div>
      )}

      {editingTask && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden">
            <div className="p-6 border-b flex justify-between items-center">
              <h2 className="text-xl font-bold text-slate-800">Edit Task</h2>
                <button onClick={() => setEditingTask(null)} className="text-slate-400 hover:text-slate-600 text-2xl">&times;</button>
            </div>
      
            <form onSubmit={handleUpdateTask} className="p-6 space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Title</label>
                <input name="title" required
                  className="w-full border rounded-xl px-4 py-2 focus:ring-2 focus:ring-indigo-500 outline-none"
                  defaultValue={editingTask.title} 
                />
              </div>
        
            <div>
              <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Description</label>
              <textarea name="description"
                className="w-full border rounded-xl px-4 py-2 h-32 focus:ring-2 focus:ring-indigo-500 outline-none"
                defaultValue={editingTask.description} 
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">Importance (1-10)</label>
                <input required name="importance" type="number" min="1" max="10" defaultValue={editingTask.importance} className="w-full border rounded-xl px-4 py-2 outline-none" />
              </div>
              <div>
                <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">Length (e.g. 30m)</label>
                <input name="length" defaultValue={editingTask.length} className="w-full border rounded-xl px-4 py-2 outline-none" />
              </div>
            </div>

            <div>
              <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">Due Date</label>
              <input name="due_at" type="datetime-local" defaultValue={editingTask.due_at ? editingTask.due_at.substring(0, 16) : ""} className="w-full border rounded-xl px-4 py-2 outline-none" />
            </div>

            <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
              <input name="reminder_enabled" type="checkbox" defaultChecked={editingTask.reminder} className="w-5 h-5 accent-indigo-600" />
              <span className="text-sm font-semibold text-slate-700">Set the reminder</span>
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
              <h2 className="text-xl font-bold text-slate-800">Create New Task</h2>
              <button onClick={() => setIsAdding(false)} className="text-slate-400 hover:text-slate-600 text-2xl">&times;</button>
            </div>
      
            <form onSubmit={handleCreateTask} className="p-6 space-y-4">
              <div>
                <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">Title</label>
                <input name="title" required placeholder="Title" className="w-full border rounded-xl px-4 py-2 outline-none focus:ring-2 focus:ring-indigo-500" />
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">Description</label>
                <textarea name="description" placeholder="Add some details..." className="w-full border rounded-xl px-4 py-2 h-20 outline-none focus:ring-2 focus:ring-indigo-500" />
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">
                  Due Date & Time
                </label>
              <input name="due_at" type="datetime-local" className="w-full border rounded-xl px-4 py-2 outline-none focus:ring-2 focus:ring-indigo-500" />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">Importance (1-10)</label>
                  <input name="importance" required type="number" min="1" max="10" placeholder="5" className="w-full border rounded-xl px-4 py-2 outline-none" />
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">Length</label>
                  <input name="length" type="number" min="0" placeholder="30" className="w-full border rounded-xl px-4 py-2 outline-none" />
                </div>
              </div>

              <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
                <input name="reminder_enabled" type="checkbox" className="w-5 h-5 accent-indigo-600" />
                  <span className="text-sm font-semibold text-slate-700">Set the reminder</span>
              </div>

              <div className="flex gap-3 pt-4">
                <button type="button" onClick={() => setIsAdding(false)} className="flex-1 px-4 py-3 rounded-xl font-bold text-slate-500 bg-slate-100">Cancel</button>
                <button type="submit" className="flex-1 px-4 py-3 rounded-xl font-bold text-white bg-indigo-600 shadow-lg shadow-indigo-200">Create Task</button>
              </div>
            </form>
          </div>
        </div>
      )}
  
    </div>
  );
}