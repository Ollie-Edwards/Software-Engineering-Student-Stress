import React from 'react';

export default function NavigationBar({onAddTask}) {
  return (
    <nav className="flex items-center justify-between px-6 py-4 bg-white border-b shadow-sm">
      
      {/* Logo */}
      <div className="flex items-center gap-2">
        <div className="text-2xl font-bold text-indigo-900">Logo</div>
      </div>

      {/* Search Bar */}
      <div className="flex-1 max-w-md mx-4">
        <input 
          type="text" 
          placeholder="Search tasks..." 
          className="w-full px-4 py-2 bg-gray-100 border rounded-lg focus:outline-none"
        />
      </div>

      {/* New Tasks button */}
      <div className="flex items-center gap-4">
        <button onClick={() => window.location.href = '/'} className="px-4 py-2 border-2 border-slate-200 hover:border-slate-300 text-slate-600 font-bold rounded-xl transition-all">
          Moodle tasks
        </button>
        <button onClick={onAddTask} className="bg-indigo-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-indigo-700">
          + New Task
        </button>
      </div>

    </nav>
  );
}