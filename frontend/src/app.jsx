import React, { useState, useEffect } from 'react';

// A component for displaying a problem with a difficulty tag
const ProblemCard = ({ problem }) => {
  const difficultyMap = { 1: 'Easy', 2: 'Medium', 3: 'Hard' };
  const difficultyClass = `difficulty-${difficultyMap[problem.difficulty]?.toLowerCase()}`;
  
  return (
    <div className="problem-card">
      <div className="problem-title">
        <span>{problem.title}</span>
        <span className={`difficulty-tag ${difficultyClass}`}>
          {difficultyMap[problem.difficulty] || 'N/A'}
        </span>
      </div>
      <p className="problem-reason">{problem.reason}</p>
    </div>
  );
};

// A component for the skills table
const SkillsTable = ({ skills }) => {
  // Sort skills from weakest to strongest to highlight areas for improvement
  const sortedSkills = Object.entries(skills).sort(([, a], [, b]) => a - b);

  return (
    <div className="panel">
      <h3>Skill Analysis</h3>
      <div className="skills-table-container">
        <table>
          <thead>
            <tr>
              <th>Concept</th>
              <th>Mastery</th>
            </tr>
          </thead>
          <tbody>
            {sortedSkills.map(([concept, score]) => (
              <tr key={concept}>
                <td>{concept}</td>
                <td>
                  <div className="mastery-bar-container">
                    <div 
                      className="mastery-bar" 
                      style={{ width: `${score * 100}%` }}
                    ></div>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

function App() {
  const [userId, setUserId] = useState('me'); // Hardcoded for this example
  const [skills, setSkills] = useState({});
  const [recommendations, setRecommendations] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError('');
      try {
        // Fetch skills data
        const skillsResponse = await fetch(`http://127.0.0.1:8000/skills/${userId}`);
        if (!skillsResponse.ok) throw new Error('Could not fetch skills. Is the backend server running?');
        const skillsData = await skillsResponse.json();
        setSkills(skillsData.skills);

        // Fetch recommendations data
        const recsResponse = await fetch(`http://127.0.0.1:8000/recommend/${userId}`);
        if (!recsResponse.ok) throw new Error('Could not fetch recommendations.');
        const recsData = await recsResponse.json();
        setRecommendations(recsData);
      } catch (err) {
        setError(err.message);
        setSkills({});
        setRecommendations([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [userId]); // Re-run this effect if userId changes

  return (
    <div className="app-container">
      <nav className="navbar">
        <h1>LeetCode Path Analyzer</h1>
      </nav>
      <main className="main-content">
        <div className="left-column">
          <div className="panel">
            <h3>Recommended For You</h3>
            {loading && <p>Loading recommendations...</p>}
            {error && <p className="error-message">{error}</p>}
            {!loading && !error && (
              <div className="recommendations-list">
                {recommendations.length > 0 ? (
                  recommendations.map((prob) => (
                    <ProblemCard key={prob.problem_id} problem={prob} />
                  ))
                ) : (
                  <p>No recommendations available.</p>
                )}
              </div>
            )}
          </div>
        </div>
        <div className="right-column">
          {!loading && !error && <SkillsTable skills={skills} />}
        </div>
      </main>
    </div>
  );
}

export default App;