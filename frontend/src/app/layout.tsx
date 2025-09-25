import React from 'react';
import './globals.css';

const Layout = ({ children }) => {
    return (
        <div className="flex">
            <div className="w-1/2">
                {children[0]} {/* Resume component will be placed here */}
            </div>
            <div className="w-1/2">
                {children[1]} {/* Chatbot component will be placed here */}
            </div>
        </div>
    );
};

export default Layout;