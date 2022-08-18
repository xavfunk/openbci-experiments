import argparse
import time
import numpy as np
from playsound import playsound


import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations


"""
This script implements a simple resting-state EEG recording, 
the user can decide to repeat several times

prep
sudo chmod a+rw /dev/ttyUSB0

activate brainflow env
source ./brainflow/bin/activate

enter this in terminal to start exp
python3.8 markers.py --board-id 0 --serial-port /dev/ttyUSB0 [+ additional args]


board channels as found out with board.get_xy_channels
package_num:0
EXG:        [1, 2, 3, 4, 5, 6, 7, 8]; ['Fp1', 'Fp2', 'C3', 'C4', 'P7', 'P8', 'O1', 'O2']
accel:      [9, 10, 11]
analog:     [19, 20, 21] 
timestamp:  22
other:      [12, 13, 14, 15, 16, 17, 18]
marker:     23
"""

def main():
    BoardShim.enable_dev_board_logger()

	# set up parser
    parser = argparse.ArgumentParser()
    # use docs to check which parameters are required for specific board, e.g. for Cyton - set serial port
    parser.add_argument('--timeout', type=int, help='timeout for device discovery or connection', required=False,
                        default=0)
    parser.add_argument('--ip-port', type=int, help='ip port', required=False, default=0)
    parser.add_argument('--ip-protocol', type=int, help='ip protocol, check IpProtocolType enum', required=False,
                        default=0)
    parser.add_argument('--ip-address', type=str, help='ip address', required=False, default='')
    parser.add_argument('--serial-port', type=str, help='serial port', required=False, default='')
    parser.add_argument('--mac-address', type=str, help='mac address', required=False, default='')
    parser.add_argument('--other-info', type=str, help='other info', required=False, default='')
    parser.add_argument('--streamer-params', type=str, help='streamer params', required=False, default='')
    parser.add_argument('--serial-number', type=str, help='serial number', required=False, default='')
    parser.add_argument('--board-id', type=int, help='board id, check docs to get a list of supported boards',
                        required=True)
    parser.add_argument('--file', type=str, help='file', required=False, default='')
    parser.add_argument('--sub', type=str, help='subject id', required=False, default='unknown')
    parser.add_argument('--drug', type=str, help='substance name', required=False, default='sober')
    parser.add_argument('--duration', type=int, help='duration of recording', required=False, default=5)

    # get params from parser
    args = parser.parse_args()
	
    params = BrainFlowInputParams()
    params.ip_port = args.ip_port
    params.serial_port = args.serial_port
    params.mac_address = args.mac_address
    params.other_info = args.other_info
    params.serial_number = args.serial_number
    params.ip_address = args.ip_address
    params.ip_protocol = args.ip_protocol
    params.timeout = args.timeout
    params.file = args.file
    # get sub id, drug, duration
    sub = args.sub
    drug = args.drug
    duration = args.duration
    
    board = BoardShim(args.board_id, params)
    board.prepare_session()
	
    condition = None
    
    # wait for key press to start
    while condition is None:
	    condition = str(input("eyes open [o] or closed [c]? press [o] or [c] and then enter to start"))

    ses_no = 1
    while True:
        # start stream
        board.start_stream(streamer_params = args.streamer_params)
        print('Measuring...')

        # resting for X minutes
        time.sleep(duration * 60)
        
        # get data, end session
        data = board.get_board_data()
        board.stop_stream()
        board.release_session()
    
        # save data
        try:
            np.save(f'data_subject-{sub}_drug-{drug}_session-{str(ses_no)}_condition-{condition}.npy', data)
        except NameError:
            np.save(f'data_session-{str(ses_no)}.npy', data)

        # playing sound to indicate X minutes are over, this could be optimized
        playsound('CYCdh_K1close_Snr-05.wav')
    
        # prompt input to decide for another round or not
        condition = str(input(f"data saved. Press [o] or [c] and then enter for another {duration} minutes, or ctrl+c to abort"))
        
        # clear answer
        condition = None

        # increase ses_no
        ses_no += 1

    return


if __name__ == "__main__":
    
    main()
    
    
    
    
    
    
    

