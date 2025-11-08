#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Setting up Screendibs development environment...${NC}"

# Create Python virtual environment
echo -e "${YELLOW}Creating Python virtual environment...${NC}"
python -m venv backend/.venv
source backend/.venv/bin/activate

# Install backend dependencies
echo -e "${YELLOW}Installing backend dependencies...${NC}"
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo -e "${YELLOW}Installing frontend dependencies...${NC}"
cd frontend
npm install
cd ..

# Set up environment files
echo -e "${YELLOW}Setting up environment files...${NC}"
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo -e "${YELLOW}Created backend/.env from example file. Please update with your actual values.${NC}"
fi

if [ ! -f frontend/.env ]; then
    cp frontend/.env.example frontend/.env
    echo -e "${YELLOW}Created frontend/.env from example file. Please update with your actual values.${NC}"
fi

# Initialize database
echo -e "${YELLOW}Initializing database...${NC}"
cd backend
alembic upgrade head
cd ..

echo -e "${GREEN}\nSetup completed!${NC}"
echo -e "\nNext steps:"
echo "1. Update backend/.env with your actual configuration values"
echo "2. Start the backend server: cd backend && uvicorn app.main:app --reload"
echo "3. Start the frontend development server: cd frontend && npm run dev"