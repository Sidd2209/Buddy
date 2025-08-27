# Deployment Guide for FreeTalk on Render

This guide will walk you through deploying your FreeTalk application to Render.

## Prerequisites

1. A GitHub, GitLab, or Bitbucket account
2. Your FreeTalk code pushed to a Git repository
3. A Render account (free tier available)

## Step 1: Prepare Your Repository

Make sure your repository contains all the necessary files:

```
Buddy/
├── render.yaml              # Render configuration
├── package.json             # Frontend dependencies
├── vite.config.js           # Vite configuration
├── backend/
│   ├── app.py              # Flask application
│   ├── requirements.txt    # Python dependencies
│   ├── user_manager.py     # User management
│   └── room_manager.py     # Room management
└── src/                    # React components
```

## Step 2: Deploy to Render

### Option A: Automatic Deployment (Recommended)

1. **Sign up/Login to Render**
   - Go to [render.com](https://render.com)
   - Sign up or log in to your account

2. **Connect Your Repository**
   - Click "New +" in your Render dashboard
   - Select "Blueprint" (this will use your render.yaml)
   - Connect your Git repository
   - Render will automatically detect the `render.yaml` file

3. **Deploy**
   - Render will create both services automatically
   - The deployment process will take 5-10 minutes
   - You'll get URLs for both frontend and backend

### Option B: Manual Deployment

#### Deploy Backend First

1. **Create Web Service**
   - Click "New +" → "Web Service"
   - Connect your Git repository

2. **Configure Backend Service**
   - **Name**: `freetalk-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && python app.py`
   - **Plan**: Free

3. **Environment Variables**
   - Add `SECRET_KEY` with a secure random string
   - Render will automatically set `PORT`

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Note the service URL (e.g., `https://freetalk-backend.onrender.com`)

#### Deploy Frontend

1. **Create Static Site**
   - Click "New +" → "Static Site"
   - Connect your Git repository

2. **Configure Frontend Service**
   - **Name**: `freetalk-frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
   - **Plan**: Free

3. **Environment Variables**
   - Add `VITE_BACKEND_URL` with your backend service URL
   - Example: `https://freetalk-backend.onrender.com`

4. **Deploy**
   - Click "Create Static Site"
   - Wait for deployment to complete

## Step 3: Test Your Deployment

1. **Test Backend**
   - Visit your backend URL
   - You should see: `{"status": "ok", "message": "FreeTalk Backend is running"}`

2. **Test Frontend**
   - Visit your frontend URL
   - The app should load and connect to the backend
   - Test video chat functionality

## Step 4: Troubleshooting

### Common Issues

1. **Backend Connection Errors**
   - Check that the backend URL in frontend environment variables is correct
   - Ensure CORS is properly configured
   - Check Render logs for errors

2. **Build Failures**
   - Check that all dependencies are in requirements.txt
   - Verify Python version compatibility
   - Check build logs in Render dashboard

3. **WebRTC Issues**
   - Ensure you're using HTTPS (Render provides this automatically)
   - Check browser console for WebRTC errors
   - Verify STUN servers are accessible

### Checking Logs

1. **Backend Logs**
   - Go to your backend service in Render dashboard
   - Click "Logs" tab
   - Look for any error messages

2. **Frontend Logs**
   - Open browser developer tools
   - Check Console tab for errors
   - Check Network tab for failed requests

## Step 5: Custom Domain (Optional)

1. **Add Custom Domain**
   - In your Render service settings
   - Go to "Settings" → "Custom Domains"
   - Add your domain and configure DNS

2. **SSL Certificate**
   - Render automatically provides SSL certificates
   - No additional configuration needed

## Environment Variables Reference

### Backend Service
```bash
SECRET_KEY=your-secure-random-string-here
PORT=3000  # Set automatically by Render
```

### Frontend Service
```bash
VITE_BACKEND_URL=https://your-backend-service.onrender.com
```

## Performance Optimization

1. **Enable Auto-Deploy**
   - Connect your Git repository
   - Render will automatically redeploy on code changes

2. **Monitor Usage**
   - Free tier has limitations
   - Monitor your service usage in Render dashboard

3. **Scale Up (if needed)**
   - Upgrade to paid plans for better performance
   - More resources and faster response times

## Security Considerations

1. **Environment Variables**
   - Never commit sensitive data to Git
   - Use Render's environment variable system

2. **HTTPS**
   - Render provides automatic HTTPS
   - Required for WebRTC camera/microphone access

3. **CORS**
   - Properly configured for production
   - Only allow necessary origins

## Support

- **Render Documentation**: [docs.render.com](https://docs.render.com)
- **Render Community**: [community.render.com](https://community.render.com)
- **FreeTalk Issues**: Check your repository issues

## Cost

- **Free Tier**: $0/month (with limitations)
- **Paid Plans**: Starting from $7/month for better performance
- **Bandwidth**: Free tier includes 750 hours/month

Your FreeTalk application should now be live and accessible to users worldwide! 🎉
