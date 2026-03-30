import mongoose from 'mongoose';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.resolve(process.cwd(), '.env') });

const atlasURL = process.env.atlas_URL;
const dbName = process.env.atlas_DB_NAME;


if (!atlasURL) {
    console.error('❌ Error: atlas_URL not found in .env file');
    process.exit(1);
}

console.log('⏳ Attempting to connect to MongoDB Atlas...');

mongoose.connect(atlasURL)
    .then(() => {
        console.log('✅ Success! Successfully connected to MongoDB Atlas.');
        process.exit(0);
    })
    .catch((err) => {
        console.error('❌ Connection Failed:', err.message);
        process.exit(1);
    });
