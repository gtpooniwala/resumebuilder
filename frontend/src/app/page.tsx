import React from 'react';
import Layout from '../components/Layout';

const HomePage = () => {
    return (
        <Layout>
            <div className="flex">
                <div className="w-1/2">
                    {/* Resume component will be rendered here */}
                </div>
                <div className="w-1/2">
                    {/* Chatbot component will be rendered here */}
                </div>
            </div>
        </Layout>
    );
};

export default HomePage;