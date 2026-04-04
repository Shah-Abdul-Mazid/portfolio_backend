import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { v2 as cloudinary } from 'cloudinary';
import dotenv from 'dotenv';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Cloudinary Configuration
cloudinary.config({
    cloud_name: process.env.CLOUDINARY_CLOUD_NAME,
    api_key: process.env.CLOUDINARY_API_KEY,
    api_secret: process.env.CLOUDINARY_API_SECRET
});

/**
 * Extracts all unique /uploads/ or cloudinary paths from a nested object or array.
 */
export const extractUploadPaths = (obj, paths = new Set()) => {
    if (!obj) return paths;

    if (typeof obj === 'string') {
        // Look for URLs containing /uploads/ (Local)
        if (obj.includes('/uploads/')) {
            const fileName = obj.split('/uploads/').pop();
            paths.add({ type: 'local', value: fileName });
        }
        // Look for GridFS URLs
        else if (obj.includes('/api/upload/')) {
            const fileId = obj.split('/api/upload/').pop();
            paths.add({ type: 'gridfs', value: fileId });
        }
        // Look for Cloudinary URLs
        else if (obj.includes('res.cloudinary.com')) {
            // Extract public_id from Cloudinary URL: ...upload/v12345/portfolio_uploads/public_id.jpg
            // We want everything after the version (v[digits]) excluding the extension
            const parts = obj.split('/upload/');
            if (parts.length > 1) {
                const afterUpload = parts[1].split('/');
                // Remove version (v12345) if present
                const pathParts = afterUpload[0].startsWith('v') && !isNaN(afterUpload[0].substring(1)) 
                    ? afterUpload.slice(1) 
                    : afterUpload;
                
                // Rejoin and remove extension
                const fullPath = pathParts.join('/');
                const publicId = fullPath.substring(0, fullPath.lastIndexOf('.')) || fullPath;
                paths.add({ type: 'cloudinary', value: publicId });
            }
        }
    } else if (Array.isArray(obj)) {
        obj.forEach(item => extractUploadPaths(item, paths));
    } else if (typeof obj === 'object') {
        Object.values(obj).forEach(val => extractUploadPaths(val, paths));
    }
    return paths;
};

/**
 * Deletes a file from the appropriate storage (local, GridFS, or Cloudinary).
 */
export const deleteUploadFile = async (item) => {
    if (!item || !item.value) return;
    
    const { type, value } = item;

    if (type === 'local') {
        const safeName = path.basename(value);
        const filePath = path.join(process.cwd(), 'uploads', safeName);
        if (fs.existsSync(filePath)) {
            try {
                fs.unlinkSync(filePath);
                console.log(`🗑️ Deleted local file: ${safeName}`);
            } catch (err) {
                console.error(`❌ Failed to delete local file ${safeName}:`, err.message);
            }
        }
    } 
    else if (type === 'cloudinary') {
        try {
            const result = await cloudinary.uploader.destroy(value);
            console.log(`🗑️ Cloudinary item deleted (${value}):`, result.result);
        } catch (err) {
            console.error(`❌ Cloudinary delete failed for ${value}:`, err.message);
        }
    }
    // GridFS deletion would require bucket access here, which might be overkill for this utility 
    // unless strictly needed. We'll stick to Local and Cloudinary for now.
};

