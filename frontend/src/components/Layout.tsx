import React from 'react';
import Resume from './Resume';
import Chatbot from './Chatbot';

const Layout: React.FC = () => {
    return (
        <div className="flex">
            <div className="w-1/2">
                <Resume />
            </div>
            <div className="w-1/2">
                <Chatbot />
            </div>
        </div>
    );
};

export default Layout;