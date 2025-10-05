#! /bin/bash

PORT=22006
MACHINE=paffenroth-23.dyn.wpi.edu
STUDENT_ADMIN_KEY_PATH=$HOME/.ssh

# Clean up from previous runs
ssh-keygen -f "~/.ssh/known_hosts" -R "[${MACHINE}]:${PORT}"
rm -rf tmp

# Check that the code is installed and start up the product
COMMAND="ssh ${STUDENT_ADMIN_KEY_PATH}/student-admin_key -p ${PORT} -o StrictHostKeyChecking=no student-admin@${MACHINE}"

${COMMAND} "git clone https://github.com/brianmorissette/Case_Study_1_Group_6.git"
${COMMAND} "ls Case_Study_1_Group_6"
${COMMAND} "sudo apt install -qq -y python3-venv"
${COMMAND} "cd Case_Study_1_Group_6 && python3 -m venv venv"
${COMMAND} "cd Case_Study_1_Group_6 && source venv/bin/activate && pip install -r requirements.txt"
${COMMAND} "nohup Case_Study_1_Group_6/venv/bin/python3 Case_Study_1_Group_6/app.py > log.txt 2>&1 &"

# Lock down machine, file with authorized keys on Linux server

# Change the permissions of the authorized keys
chmod 600 authorized_keys

echo "checking that the authorized_keys file is correct"
ls -l authorized_keys
cat authorized_keys

# Copy the authorized_keys file to the server
scp -i student-admin_key -P ${PORT} -o StrictHostKeyChecking=no authorized_keys student-admin@${MACHINE}:~/.ssh/

# Check the key file on the server
echo "checking that the authorized_keys file is correct"
ssh -p ${PORT} -o StrictHostKeyChecking=no student-admin@${MACHINE} "cat ~/.ssh/authorized_keys"

# Copy the authorized_keys file to the server
scp -i student-admin_key -P ${PORT} -o StrictHostKeyChecking=no authorized_keys student-admin@${MACHINE}:~/.ssh/

# Check the key file on the server
echo "checking that the authorized_keys file is correct"
cd ~/.ssh
ssh -i group6-vm_key -p ${PORT} -o StrictHostKeyChecking=no student-admin@${MACHINE} "cat ~/.ssh/authorized_keys"