import mongoose from 'mongoose';
import dotenv from 'dotenv';
import Visitor from './models/Visitor.js';
import Analytics from './models/Analytics.js';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config();

async function clearVisitors() {
    try {
        // Find MONGODB_URI. If not in .env, check config/db.js or assume local.
        const uri = process.env.MONGODB_URI || 'mongodb://localhost:27017/portfolio_data';
        
        await mongoose.connect(uri);
        console.log('Connected to MongoDB');

        const vResult = await Visitor.deleteMany({});
        const aResult = await Analytics.findOneAndUpdate({ id: 'total_views' }, { count: 0 });

        console.log(`Cleared ${vResult.deletedCount} visitors.`);
        console.log(`Reset total views count.`);

        await mongoose.disconnect();
        console.log('Disconnected from MongoDB');
        process.exit(0);
    } catch (err) {
        console.error('Error clearing data:', err.message);
        process.exit(1);
    }
}

clearVisitors();
