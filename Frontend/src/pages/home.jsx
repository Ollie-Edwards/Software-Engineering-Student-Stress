import React, { useEffect, useState } from "react";

export default function Home() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchTasks() {
      try {
        const res = await fetch("http://localhost:8000/tasks");
        if (!res.ok) throw new Error("Failed to fetch tasks");
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

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-bold">Tasks</h1>
      {tasks.length === 0 && <p>No tasks found.</p>}
      <div className="grid gap-4">
        {tasks.map((task) => (
          <div key={task.id} className="p-4 border rounded-xl shadow-sm">
            <h2 className="text-xl font-semibold">{task.title}</h2>
            <p className="text-gray-700">{task.description}</p>
            <p className="mt-2">
              <strong>Status:</strong> {task.status ? "Completed" : "Not Completed"}
            </p>
            <p>
              <strong>Importance:</strong> {task.importance}
            </p>
            <p>
              <strong>Length:</strong> {task.length}
            </p>
            <p>
              <strong>Tag ID:</strong> {task.tag_id}
            </p>
            <p>
              <strong>Due At:</strong> {new Date(task.due_at).toLocaleString()}
            </p>
            <p>
              <strong>Created At:</strong> {new Date(task.created_at).toLocaleString()}
            </p>
            <p>
              <strong>Updated At:</strong> {new Date(task.updated_at).toLocaleString()}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}