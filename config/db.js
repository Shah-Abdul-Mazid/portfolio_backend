import mongoose from 'mongoose';

const connectDB = async () => {
    try {
        const atlasURL = process.env.atlas_URL;
        if (!atlasURL) throw new Error('atlas_URL not found in environment');
        const dbName = process.env.atlas_DB_NAME || 'portfolio_data';
        await mongoose.connect(atlasURL, { dbName });
        console.log(`✅ Connected to MongoDB Database: ${dbName}`);
    } catch (err) {
        console.error('⚠️ MongoDB Connection Error:', err.message);
        console.log('🔄 Proceeding in MOCK MODE (Local Memory)');
    }
};

export default connectDB;
