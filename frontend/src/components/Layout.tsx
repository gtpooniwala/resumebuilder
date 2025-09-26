import React from 'react';
import Resume from './Resume';
import Chatbot from './Chatbot';

const Layout: React.FC = () => {
    const handleNewSession = () => {
        // TODO: Implement new session logic
        console.log('Starting new chat session...');
    };

    const handleShowHistory = () => {
        // TODO: Implement show history logic
        console.log('Showing chat history...');
    };

    return (
        <div className="flex">
            <div className="w-1/2">
                <Resume />
            </div>
            <div className="w-1/2">
                <Chatbot 
                    onNewSession={handleNewSession}
                    onShowHistory={handleShowHistory}
                />
            </div>
        </div>
    );
};

export default Layout;
