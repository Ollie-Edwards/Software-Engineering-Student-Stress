import { Link, useLocation, useNavigate } from 'react-router-dom';

function NavigationBar({ onAddTask }) {
  const location = useLocation();
  const navigate = useNavigate();
  
  const isMoodlePage = location.pathname === '/moodle';

  return (
    <nav className="flex items-center justify-between p-4 bg-white border-b">
      <div className="text-indigo-600 font-bold text-xl">Logo</div>
      <input 
        type="text" 
        placeholder="Search tasks..." 
        className="border rounded-lg px-4 py-2 w-1/3 bg-slate-50"
      />

      <div className="flex items-center gap-4">
        {isMoodlePage ? (
          <button 
            onClick={() => navigate('/')} 
            className="px-4 py-2 border-2 border-slate-200 hover:bg-slate-50 text-slate-600 font-bold rounded-xl transition-all"
          >
            ← Back to Main
          </button>
        ) : (
          <>
            <Link to="/moodle">
              <button className="px-4 py-2 border-2 border-slate-200 hover:border-slate-300 text-slate-600 font-bold rounded-xl transition-all">
                Moodle tasks
              </button>
            </Link>
            <button 
              onClick={onAddTask} 
              className="bg-indigo-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-indigo-700 transition-all"
            >
              + New Task
            </button>
          </>
        )}
      </div>
    </nav>
  );
}

export default NavigationBar;