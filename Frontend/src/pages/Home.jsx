import React, { useEffect, useState, useRef } from "react";
import LinkButton from '../components/LinkElement';


//  VERY IMPORTANT MESSAGE

// ***THIS IS NOT FOR SUBMISSION OR MERGE TO MAIN***, THIS IS ONLY FOR
// FACILITATING DATA COLLECTION FOR THE STUDY, and will be removed after use.



// ── Experiment phases ──────────────────────────────────────────────
// "instructions" → "ui" → "black" → "likert" → "done"

const LIKERT_QUESTION = "I felt overwhelmed while deciding which task to complete next";
const LIKERT_QUESTION_2 = "I felt stressed while deciding which task to complete next"

// ── Taskcard (unchanged) ───────────────────────────────────────────
const Taskcard = ({task, setTasks, setEditingTask, handleDeleteTask, fetchTasks}) => {
  const isHigh   = task.priority >= 70;
  const isMedium = task.priority >= 40 && task.priority < 70;

  const barColor     = isHigh ? 'bg-red-500'     : isMedium ? 'bg-amber-400'    : 'bg-emerald-500';
  const badgeBg      = isHigh ? 'bg-red-100'     : isMedium ? 'bg-amber-100'    : 'bg-emerald-100';
  const badgeText    = isHigh ? 'text-red-700'   : isMedium ? 'text-amber-700'  : 'text-emerald-700';
  const priorityLabel= isHigh ? 'High'           : isMedium ? 'Medium'          : 'Low';

  const [showSubtasks,     setShowSubtasks]     = useState(false);
  const [tempSubtaskTitle, setTempSubtaskTitle] = useState("");
  const [newSubtaskTitle,  setNewSubtaskTitle]  = useState("");
  const [isAddingSubtask,  setIsAddingSubtask]  = useState(false);

  const toggleComplete = async (e) => {
    e.stopPropagation();
    const currentlyCompleted = task.completed;
    const newStatus = !currentlyCompleted;
    setTasks(prev => prev.map(t =>
      t.id === task.id ? { ...t, completed: newStatus, subtasks: t.subtasks.map(st => ({ ...st, completed: newStatus })) } : t
    ));
    try {
      const res = await fetch(`http://localhost:8000/tasks/task/${task.id}/${newStatus ? 'complete' : 'reopen'}`, { method: 'POST' });
      if (!res.ok) throw new Error("Database update failed");
    } catch (err) {
      console.error(err);
      setTasks(prev => prev.map(t =>
        t.id === task.id ? { ...t, completed: currentlyCompleted, subtasks: t.subtasks.map(st => ({ ...st, completed: currentlyCompleted })) } : t
      ));
    }
  };

  return (
    <React.Fragment key={task.id}>
      <div key={task.id} onClick={() => setEditingTask(task)} className="cursor-pointer relative flex border rounded-2xl shadow-sm overflow-hidden bg-white">
        <div className={`w-2 shrink-0 ${barColor}`} />
        <div title="Task Modal" className="p-5 flex-1 flex flex-col gap-3">
          <div className="flex justify-between items-start">
            <div>
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase mb-1 inline-block ${badgeBg} ${badgeText}`}>
                • {priorityLabel} ({task.priority})
              </span>
              <h2 className="text-xl font-bold text-slate-800 leading-tight">{task.title}</h2>
            </div>
            <div className="flex items-center gap-1">
              <LinkButton url={task.reference_url} />
              <button onClick={toggleComplete} title="Toggle Complete Task" className="focus:outline-none transition-transform active:scale-90">
                {task.completed ? (
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 text-slate-400 hover:text-black">
                    <rect x="3" y="3" width="18" height="18" rx="3" /><path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75" />
                  </svg>
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 text-slate-400 hover:text-black">
                    <rect x="3" y="3" width="18" height="18" rx="3" />
                  </svg>
                )}
              </button>
              <button onClick={(e) => { e.stopPropagation(); handleDeleteTask(task.id); }} className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors rounded-lg" title="Delete Task">
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
              <button title="Toggle Subtasks" onClick={(e) => { e.stopPropagation(); setShowSubtasks(!showSubtasks); }} className="p-1 hover:bg-slate-100 rounded transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" className={`h-5 w-5 transform transition-transform ${showSubtasks ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>
          </div>

          <p className="text-slate-600 text-sm line-clamp-2">{task.description}</p>

          <div className="grid grid-cols-3 gap-y-2 gap-x-4 pt-4 border-t mt-auto text-xs text-slate-500">
            <p><strong>Importance:</strong> {task.importance}</p>
            <p><strong>Length:</strong> {task.length} mins</p>
            <p><strong>Due In:</strong> {task.due_at ? (() => {
              const diff = new Date(task.due_at) - new Date();
              if (diff < 0) return "Overdue";
              const days  = Math.floor(diff / (1000 * 60 * 60 * 24));
              const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
              return days > 0 ? `${days}d ${hours}h` : `${hours}h`;
            })() : "N/A"}</p>
          </div>
        </div>
      </div>

     
    </React.Fragment>
  );
};

// ── Static task data ───────────────────────────────────────────────
const INITIAL_TASKS = [
  {
    id: 1, user_id: 1,
    title: "Algorithms & Complexity - Exam Revision",
    description: "Revise dynamic programming, graph traversal algorithms, and NP-completeness proofs. Focus on past paper questions from 2023-2025.",
    completed: false, importance: 9, length: 120,
    tags: ["Revision", "urgent"],
    due_at: "2026-04-30T09:00:00.000000",
    reference_url: "https://moodle.bath.ac.uk/course/section.php?id=112847",
    priority: 88,
    created_at: "2026-04-29T09:00:00.000000", updated_at: "2026-04-29T09:00:00.000000",
    subtasks: []
  },
  {
    id: 2, user_id: 1,
    title: "Distributed Systems - Consensus Protocol Essay",
    description: "Write a 2000 word critical analysis comparing Raft and Paxos consensus algorithms, covering fault tolerance and real-world trade-offs.",
    completed: false, importance: 7, length: 150,
    tags: ["Coursework"],
    due_at: "2026-05-05T17:00:00.000000",
    reference_url: "https://moodle.bath.ac.uk/course/section.php?id=198423",
    priority: 62,
    created_at: "2026-04-29T09:00:00.000000", updated_at: "2026-04-29T09:00:00.000000",
    subtasks: []
  },
  {
    id: 3, user_id: 1,
    title: "Database Systems - Normalisation Problem Sheet",
    description: "Complete the third normal form and BCNF decomposition exercises from the week 9 problem sheet. Check answers against the model solutions.",
    completed: false, importance: 5, length: 60,
    tags: ["Coursework"],
    due_at: "2026-05-07T17:00:00.000000",
    reference_url: "https://moodle.bath.ac.uk/course/section.php?id=217834",
    priority: 44,
    created_at: "2026-04-29T09:00:00.000000", updated_at: "2026-04-29T09:00:00.000000",
    subtasks: []
  },
  {
    id: 4, user_id: 1,
    title: "Computer Vision - Lab Report Writeup",
    description: "Document the edge detection and image segmentation experiments from last week's lab. Include result figures and evaluation.",
    completed: false, importance: 5, length: 90,
    tags: ["Coursework"],
    due_at: "2026-05-09T17:00:00.000000",
    reference_url: "https://moodle.bath.ac.uk/course/section.php?id=203561",
    priority: 39,
    created_at: "2026-04-29T09:00:00.000000", updated_at: "2026-04-29T09:00:00.000000",
    subtasks: []
  },
  {
    id: 5, user_id: 1,
    title: "Book a dentist appointment",
    description: "Been putting this off for months. Just call and book in for a check-up sometime in May.",
    completed: false, importance: 3, length: 10,
    tags: ["personal", "admin"],
    due_at: "2026-05-03T12:00:00.000000",
    reference_url: null,
    priority: 17,
    created_at: "2026-04-29T09:00:00.000000", updated_at: "2026-04-29T09:00:00.000000",
    subtasks: []
  },
  {
    id: 6, user_id: 1,
    title: "Find a new Spotify playlist",
    description: "Current study playlist is getting stale. Spend a few minutes browsing for something new.",
    completed: false, importance: 1, length: 10,
    tags: ["personal"],
    due_at: null,
    reference_url: null,
    priority: 3,
    created_at: "2026-04-29T09:00:00.000000", updated_at: "2026-04-29T09:00:00.000000",
    subtasks: []
  },
];

// ── Experiment overlay components ──────────────────────────────────
function InstructionScreen({ onReady }) {
  return (
    <div
      className="fixed inset-0 bg-black flex flex-col items-center justify-center z-50 cursor-pointer select-none"
      onClick={onReady}
    >
      <div className="max-w-lg text-center space-y-6 px-8">
        <h1 className="text-white text-4xl font-bold tracking-tight">Task Study (A)</h1>
        <h4 className="text-white text-xl font-bold tracking-tight">Task instructions</h4>
        <div className="text-slate-300 text-base leading-relaxed space-y-3">
          <ul className="text-left text-white list-disc pl-5 space-y-2">
            <li>You will be shown a task management interface.</li>
            <li>Imagine these are tasks that you need to complete.</li>
            <li>Look at the tasks and decide which one you would work on next.</li>
            <li>Think about doing this as fast as you can comfortably make a decision.</li>
            <li>Once you have made your decision, <strong className="text-white">click anywhere</strong> on the screen.</li>
          </ul>
        </div>
        <div className="pt-4">
          <span className="inline-block border border-slate-500 text-slate-400 text-sm px-6 py-2 rounded-full">
            Click anywhere when ready
          </span>
        </div>
      </div>
    </div>
  );
}

function LikertScreen({ onSubmit }) {
  const [score1, setScore1] = useState(null);
  const [score2, setScore2] = useState(null);

  const labels1 = [
    { value: 1, text: "Strongly Disagree" },
    { value: 2, text: "Disagree  " },
    { value: 3, text: "Somewhat Disagree" },
    { value: 4, text: "Neutral" },
    { value: 5, text: "Somewhat Agree" },
    { value: 6, text: "Agree" },
    { value: 7, text: "Strongly Agree" },
  ];

  const labels2 = [
    { value: 1, text: "Strongly Disagree" },
    { value: 2, text: "Disagree  " },
    { value: 3, text: "Somewhat Disagree" },
    { value: 4, text: "Neutral" },
    { value: 5, text: "Somewhat Agree" },
    { value: 6, text: "Agree" },
    { value: 7, text: "Strongly Agree" },
  ];
  const renderScale = (question, selected, setSelected, labels) => (
    <div className="space-y-4">
      <p className="text-white text-xl font-medium leading-snug">{question}</p>
      <div className="flex justify-between gap-3">
        {labels.map(({ value, text }) => (
          <button
            key={value}
            onClick={() => setSelected(value)}
            className={`flex-1 flex flex-col items-center gap-2 py-4 rounded-xl border transition-all
              ${selected === value
                ? 'border-indigo-400 bg-indigo-600 text-white'
                : 'border-slate-600 bg-slate-900 text-slate-300 hover:border-slate-400'}`}
          >
            <span className="text-2xl font-bold">{value}</span>
            <span className="text-[10px] uppercase tracking-wide leading-tight">{text}</span>
          </button>
        ))}
      </div>
    </div>
  );

  return (
    <div className="fixed inset-0 bg-black flex flex-col items-center justify-center z-50 px-8">
      <div className="max-w-xl w-full text-center space-y-10">
        {renderScale(LIKERT_QUESTION, score1, setScore1, labels1)}
        {renderScale(LIKERT_QUESTION_2, score2, setScore2, labels2)}
        <button
          disabled={score1 === null || score2 === null}
          onClick={() => onSubmit(score1, score2)}
          className="px-10 py-3 rounded-full font-bold text-sm transition-all
            disabled:opacity-30 disabled:cursor-not-allowed
            bg-indigo-600 hover:bg-indigo-500 text-white"
        >
          Submit
        </button>
      </div>
    </div>
  );
}

// ── Main export ────────────────────────────────────────────────────
export default function Home({ isAdding, setIsAdding }) {
  const [tasks, setTasks]             = useState(INITIAL_TASKS);
  const [editingTask, setEditingTask] = useState(null);
  const [sortOrder, setSortOrder]     = useState("desc");

  // Experiment state: "instructions" | "ui" | "black" | "likert" | "done"
  const [phase, setPhase]   = useState("instructions");
  const uiShownAt           = useRef(null);

  const fetchTasks      = () => {};
  const uncompletedTasks = tasks.filter(t => !t.completed);
  const completedTasks   = tasks.filter(t => t.completed);

  // Phase transitions
  const handleReady = () => {
    uiShownAt.current = performance.now();
    setPhase("ui");
  };

  const handleUiClick = () => {
    if (phase !== "ui") return;
    const elapsed = ((performance.now() - uiShownAt.current)).toFixed(3);
    console.log(`[Experiment] Time to decision: ${elapsed}ms`);
    setPhase("likert");
  };

const handleLikertSubmit = (score1, score2) => {
  console.log(`[Experiment] Likert Q1 (overwhelmed): ${score1}/7`);
  console.log(`[Experiment] Likert Q2 (stressed): ${score2}/7`);
  setPhase("done");
};

  const handleUpdateTask = async (e) => {
    e.preventDefault();
    const formData   = new FormData(e.target);
    const updatedData = {
      title:            formData.get('title'),
      description:      formData.get('description'),
      importance:       parseInt(formData.get('importance')) || 0,
      length:           parseInt(formData.get('length')) || null,
      reminder_enabled: formData.get('reminder') === 'on',
    };
    try {
      const res = await fetch(`http://localhost:8000/tasks/${editingTask.id}`, {
        method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(updatedData),
      });
      if (res.ok) { setTasks(prev => prev.map(t => t.id === editingTask.id ? { ...t, ...updatedData } : t)); setEditingTask(null); }
    } catch (err) { console.error("Update failed:", err); }
  };

  const handleCreateTask = (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const newTask  = {
      id:         Date.now(), user_id: 1,
      title:      formData.get('title'),
      description:formData.get('description'),
      importance: parseInt(formData.get('importance')) || 5,
      length:     parseInt(formData.get('length')) || null,
      due_at:     formData.get('due_at') ? new Date(formData.get('due_at')).toISOString() : null,
      priority:   parseInt(formData.get('importance')) * 6 || 30,
      completed: false, tags: [], subtasks: [],
      created_at: new Date().toISOString(), updated_at: new Date().toISOString(),
    };
    setTasks(prev => [...prev, newTask]);
    setIsAdding(false);
  };

  const handleDeleteTask = (taskId) => {
    if (!window.confirm("Are you sure you want to delete this task?")) return;
    setTasks(prev => prev.filter(t => t.id !== taskId));
    if (editingTask?.id === taskId) setEditingTask(null);
  };

  const sortedUncompleted = [...uncompletedTasks].sort((a, b) =>
    sortOrder === "desc" ? b.priority - a.priority : a.priority - b.priority
  );
  const sortedCompleted = [...completedTasks].sort((a, b) =>
    sortOrder === "desc" ? b.priority - a.priority : a.priority - b.priority
  );

  return (
    <>
      {/* ── Experiment overlays ── */}
      {phase === "instructions" && <InstructionScreen onReady={handleReady} />}
      {phase === "likert"       && <LikertScreen onSubmit={handleLikertSubmit} />}
      {phase === "done"         && (
        <div className="fixed inset-0 bg-black flex items-center justify-center z-50">
          <p className="text-slate-500 text-sm">Session complete. Thank you.</p>
        </div>
      )}

      {/* ── UI (visible only during "ui" phase, click dismisses it) ── */}
      <div
        className={phase === "ui" ? "block" : "hidden"}
        onClick={handleUiClick}
      >
        <div className="p-6 max-w-250 mx-auto space-y-4">
          <div className="flex justify-between items-end mb-8">
            <div>
              <h1 className="text-3xl font-bold text-slate-900">Tasks</h1>
              <p className="text-slate-500 mt-1">
                You have <span className="font-semibold text-indigo-600">{uncompletedTasks.length}</span> tasks remaining.
              </p>
            </div>
            <div className="flex items-center gap-2 bg-white border px-3 py-1.5 rounded-lg shadow-sm">
              <span className="text-xs font-bold text-slate-400 uppercase">Sort By</span>
              <select
                className="text-xs text-slate-600 font-semibold bg-transparent focus:outline-none cursor-pointer"
                value={sortOrder}
                onChange={e => setSortOrder(e.target.value)}
                onClick={e => e.stopPropagation()}
              >
                <option value="desc">Highest to Lowest priority</option>
                <option value="asc">Lowest to Highest priority</option>
              </select>
            </div>
          </div>

          {uncompletedTasks.length === 0 && <p>No tasks found.</p>}
          <div className="grid gap-4">
            {sortedUncompleted.map(task => (
              <Taskcard key={task.id} task={task} setTasks={setTasks}
                setEditingTask={setEditingTask} handleDeleteTask={handleDeleteTask} fetchTasks={fetchTasks} />
            ))}
          </div>

          {completedTasks.length > 0 && (
            <div className="mt-12 space-y-4 pt-8 border-t border-dashed">
              <h1 className="text-3xl font-bold text-slate-900">Completed</h1>
              <p className="text-slate-500 mt-1">
                You have completed <span className="font-semibold text-indigo-600">{completedTasks.length}</span> tasks.
              </p>
              <div className="grid gap-4">
                {sortedCompleted.map(task => (
                  <Taskcard key={task.id} task={task} setTasks={setTasks}
                    setEditingTask={setEditingTask} handleDeleteTask={handleDeleteTask} fetchTasks={fetchTasks} />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}