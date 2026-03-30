import nodemailer from 'nodemailer';
import dotenv from 'dotenv';
import path from 'path';

dotenv.config();

const transporter = nodemailer.createTransport({
    host: 'smtp.gmail.com',
    port: 587,
    secure: false, // true for 465, false for 587
    auth: {
        user: process.env.GMAIL_USER,
        pass: process.env.GMAIL_PASS
    }
});

const mailOptions = {
    from: `"Test Support" <${process.env.GMAIL_USER}>`,
    to: process.env.GMAIL_USER, // Send to self
    subject: 'Nodemailer Test',
    text: 'If you see this, Nodemailer is working!'
};

console.log('⏳ Attempting to send test email...');

transporter.sendMail(mailOptions)
    .then((info) => {
        console.log('✅ Success! Email sent:', info.response);
        process.exit(0);
    })
    .catch((err) => {
        console.error('❌ Failed to send email:', err);
        process.exit(1);
    });
