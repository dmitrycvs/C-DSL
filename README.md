# C-DSL

C-DSL is a domain-specific language (DSL) designed for drawing 2D figures.  
This project utilizes ANTLR for grammar processing and requires specific versions of Python, Pip, and Java.  

## Prerequisites  

Ensure your system meets the following requirements before installation:  

- **Python**: `>=3.8`  
- **Pip**: `>=21.0`  
- **Java**: `>=11` (required for ANTLR)  

To check your current versions, run:  

```bash
python --version
pip --version
java -version
```

## Installation

To install C-DSL and set up the environment, follow these steps:

1. **Clone Repository**
```bash
git clone https://github.com/dmitrycvs/C-DSL.git
cd C-DSL
```

2. **Run the installation script**
```bash
chmod +x install.sh
./install.sh
```
or
```bash
bash install.sh
```

This script will:
- Install necessary Python dependencies
- Download and configure ANTLR
- Set up environment variables
