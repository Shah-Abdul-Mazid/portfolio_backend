import Analytics from '../models/Analytics.js';

export const trackPageView = async (req, res) => {
    try {
        const result = await Analytics.findOneAndUpdate(
            { id: 'total_views' },
            { $inc: { count: 1 } },
            { upsert: true, new: true }
        );
        res.json(result);
    } catch (err) {
        console.error('Error tracking visit:', err.message);
        res.status(500).json({ error: 'Failed to track visit' });
    }
};

export const getAnalytics = async (req, res) => {
    try {
        const result = await Analytics.findOne({ id: 'total_views' });
        res.json(result || { count: 0 });
    } catch (err) {
        console.error('Error fetching analytics:', err.message);
        res.status(500).json({ error: 'Failed to fetch analytics' });
    }
};
