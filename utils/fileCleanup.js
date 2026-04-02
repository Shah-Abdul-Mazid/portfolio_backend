import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Extracts all unique /uploads/ paths from a nested object or array.
 */
export const extractUploadPaths = (obj, paths = new Set()) => {
    if (!obj) return paths;

    if (typeof obj === 'string') {
        // Look for URLs containing /uploads/
        // Matches both local paths and URLs if they contain our prefix
        if (obj.includes('/uploads/')) {
            const fileName = obj.split('/uploads/').pop();
            paths.add(fileName);
        }
    } else if (Array.isArray(obj)) {
        obj.forEach(item => extractUploadPaths(item, paths));
    } else if (typeof obj === 'object') {
        Object.values(obj).forEach(val => extractUploadPaths(val, paths));
    }
    return paths;
};

/**
 * Deletes a file from the uploads directory if it exists.
 */
export const deleteUploadFile = (fileName) => {
    if (!fileName) return;
    
    // Safety check: ensure no path traversal
    const safeName = path.basename(fileName);
    const filePath = path.join(process.cwd(), 'uploads', safeName);
    
    if (fs.existsSync(filePath)) {
        try {
            fs.unlinkSync(filePath);
            console.log(`🗑️ Deleted unused file: ${safeName}`);
        } catch (err) {
            console.error(`❌ Failed to delete file ${safeName}:`, err.message);
        }
    }
};
