import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import LinkButton from './components/linkElement';

const MoodleTasks = () => {
    const [tasks, setTasks] = useState([]);
    const [error, setError] = useState(null);
    const navigate = useNavigate()

    useEffect(() => {
        fetch('http://localhost:8000/moodletasks')
            .then(response => {
                if (!response.ok) throw new Error('No Moodle tasks found');
                return response.json();
            })
            .then(data => setTasks(data))
            .catch(err => setError(err.message));
    }, []);

    return (
    <div className="p-6 bg-slate-50 min-h-screen">
        <h1 className="text-2xl font-bold text-slate-800 mb-6">Moodle Tasks</h1>
    
        <div className="grid gap-4">
        {tasks.map((task) => (
            <div key={task.id} className="bg-white border-l-4 border-orange-500 rounded-xl shadow-sm p-5 hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-2">
                <div>
                <span className="text-xs font-bold uppercase tracking-wider text-orange-600 bg-orange-50 px-2 py-1 rounded">
                    {task.activity}
                </span>
                <h3 className="text-lg font-bold text-slate-900 mt-2">{task.title}</h3>
                </div>
                <LinkButton url={task.reference_url}/>
            </div>

            <p className="text-slate-600 text-sm mb-4 italic">{task.course_name}</p>

            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-100 text-xs text-slate-500">
                <div>
                <p><strong>Status:</strong> {task.approved ? "Completed" : "Pending"}</p>
                </div>
                <div className="text-right">
                    <button onClick={() => handleStatusUpdate(task.id, true)} className="p-2 bg-green-50 text-green-600 rounded-lg hover:bg-green-600 hover:text-white transition-all border border-green-200" title="Approve Task">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                    </button>
    
                    <button onClick={() => handleStatusUpdate(task.id, false)} className="p-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-600 hover:text-white transition-all border border-red-200" title="Reject Task">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                        </svg>
                    </button>
                </div>
            </div>
            </div>
        ))}
        </div>
    </div>
    );
};

export default MoodleTasks;