# audiofone
Stand-alone phone audio interface.

# Have:

raspberry pi
- running raspbian lite
- ssh enabled with default pi/raspberry login
-- can do this by touching ssh file on boot partition

local:
  update deploy/hosts for correct pibox ip address
  ansible-playbook -i deploy/hosts playbook.yml

to test on pi:
  sudo /opt/futel/src/hookswitch.py
  watch stdout
  short gpio pin 7 to gpio ground
