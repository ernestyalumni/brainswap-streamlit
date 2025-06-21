#!/bin/bash

# Initialize and update git submodules
echo "Initializing git submodules..."
git submodule update --init --recursive

# Verify the MoreGroq path exists
if [ -d "submodules/InServiceOfX/PythonLibraries/ThirdParties/APIs/MoreGroq" ]; then
    echo "✅ MoreGroq library found successfully"
else
    echo "❌ MoreGroq library not found"
    exit 1
fi 