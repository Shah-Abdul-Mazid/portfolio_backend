import mongoose from 'mongoose';

const connectDB = async () => {
    try {
        const atlasURL = process.env.atlas_URL;
        await mongoose.connect(atlasURL, { dbName: process.env.atlas_DB_NAME });
        console.log(`✅ Connected to MongoDB Database: ${process.env.atlas_DB_NAME}`);
    } catch (err) {
        console.error('❌ MongoDB Connection Error:', err.message);
        process.exit(1);
    }
};

export default connectDB;
