# --- Stage 1: Build ---
FROM node:22 AS build
WORKDIR /app

# Copy dependency files and install (uses caching efficiently)
COPY package*.json ./
RUN npm install

# Copy the rest of the source and build
COPY . .
RUN npm run build

# --- Stage 2: Serve with a lightweight web server ---
FROM node:22-slim
WORKDIR /app

# Install serve to serve the production build
RUN npm install -g serve

# Copy the built frontend from the previous stage
COPY --from=build /app/dist ./dist

EXPOSE 5173

# Serve the production build
CMD ["serve", "-s", "dist", "-l", "5173"]


