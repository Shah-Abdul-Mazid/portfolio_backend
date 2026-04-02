import mongoose from 'mongoose';

const connectDB = async () => {
    try {
        const atlasURL = process.env.atlas_URL;
        if (!atlasURL) throw new Error('atlas_URL not found in environment');
        await mongoose.connect(atlasURL, { dbName: process.env.atlas_DB_NAME });
        console.log(`✅ Connected to MongoDB Database: ${process.env.atlas_DB_NAME}`);
    } catch (err) {
        console.error('⚠️ MongoDB Connection Error:', err.message);
        console.log('🔄 Proceeding in MOCK MODE (Local Memory)');
    }
};

export default connectDB;
