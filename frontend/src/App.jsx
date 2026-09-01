import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import DashboardPage from './pages/DashboardPage';
import NewResearchPage from './pages/NewResearchPage';
import LiveTrackerPage from './pages/LiveTrackerPage';
import ResultsPage from './pages/ResultsPage';
import KnowledgeSearchPage from './pages/KnowledgeSearchPage';
import HistoryPage from './pages/HistoryPage';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedProjectId, setSelectedProjectId] = useState(null);

  const handleSelectProject = (projectId) => {
    setSelectedProjectId(projectId);
  };

  return (
    <div className="app-container">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="main-content">
        <Header 
          activeTab={activeTab} 
          setActiveTab={setActiveTab} 
          onRefresh={() => window.location.reload()}
        />

        {activeTab === 'dashboard' && (
          <DashboardPage 
            setActiveTab={setActiveTab} 
            onSelectProject={handleSelectProject} 
          />
        )}

        {activeTab === 'new-research' && (
          <NewResearchPage 
            setActiveTab={setActiveTab} 
            onSelectProject={handleSelectProject} 
          />
        )}

        {activeTab === 'tracker' && (
          <LiveTrackerPage 
            projectId={selectedProjectId} 
            setActiveTab={setActiveTab} 
          />
        )}

        {activeTab === 'results' && (
          <ResultsPage 
            projectId={selectedProjectId} 
            setActiveTab={setActiveTab} 
          />
        )}

        {activeTab === 'knowledge-search' && (
          <KnowledgeSearchPage 
            setActiveTab={setActiveTab} 
            onSelectProject={handleSelectProject} 
          />
        )}

        {activeTab === 'history' && (
          <HistoryPage 
            setActiveTab={setActiveTab} 
            onSelectProject={handleSelectProject} 
          />
        )}
      </main>
    </div>
  );
}
