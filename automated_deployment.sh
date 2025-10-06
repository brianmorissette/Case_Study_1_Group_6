#! /bin/bash

PORT=22006
MACHINE=paffenroth-23.dyn.wpi.edu
STUDENT_ADMIN_KEY_PATH=$HOME/.ssh

# Clean up from previous runs
ssh-keygen -f "/home/bmorissette/.ssh/known_hosts" -R "[${MACHINE}]:${PORT}"
rm -rf tmp

# Create a temporary directory
mkdir tmp

# Copy the key to the temporary directory
cp ${STUDENT_ADMIN_KEY_PATH}/student-admin_key* tmp

# Change the premissions of the directory
chmod 700 tmp

# Change to the temporary directory
cd tmp

# Set the permissions of the key
chmod 600 student-admin_key*

# Create a unique key
rm -f my_key*
ssh-keygen -f my_key -t ed25519 -N "careful"

# Insert the key into an authorized_keys file on the server
cat my_key.pub >authorized_keys

# Change the permissions of the key
chmod 600 authorized_keys

echo "checking that the authorized_keys file is correct"
ls -l authorized_keys
cat authorized_keys

# Copy the authorized_keys file to the server
scp -i student-admin_key -P ${PORT} -o StrictHostKeyChecking=no authorized_keys student-admin@${MACHINE}:~/.ssh/

# Add the key to the ssh-agent
eval "$(ssh-agent -s)"
ssh-add my_key

# Check the key file on the server
echo "checking that the authorized_keys file is correct"
ssh -p ${PORT} -o StrictHostKeyChecking=no student-admin@${MACHINE} "cat ~/.ssh/authorized_keys"

# Check that the code is installed and start up the product
COMMAND="ssh -p ${PORT} -o StrictHostKeyChecking=no student-admin@${MACHINE}"

${COMMAND} "git clone https://github.com/brianmorissette/Case_Study_1_Group_6.git"
${COMMAND} "ls Case_Study_1_Group_6"
${COMMAND} "sudo apt install -qq -y python3-venv"
${COMMAND} "cd Case_Study_1_Group_6 && python3 -m venv venv"
${COMMAND} "cd Case_Study_1_Group_6 && source venv/bin/activate && pip install -r requirements.txt"

# Copy Hugging Face Token to VM
scp -i my_key -P ${PORT} -o StrictHostKeyChecking=no authorized_keys student-admin@${MACHINE}:~

${COMMAND} "nohup Case_Study_1_Group_6/venv/bin/python3 Case_Study_1_Group_6/app.py > log.txt 2>&1 &"
