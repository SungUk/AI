#pip3 install opencv-python
import socket
import cv2
import struct # 바이트(bytes) 형식의 데이터 처리 모듈
import pickle # 객체의 직렬화 및 역직렬화 지원 모듈

# 서버의 주소입니다. hostname 또는 ip address를 사용할 수 있습니다.
HOST='10.10.10.110'
# 서버에서 지정해 놓은 포트 번호입니다.
PORT = 4444

# 소켓 객체를 생성합니다.
# 주소 체계(address family)로 IPv4, 소켓 타입으로 TCP 사용합니다.
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

# bind 함수는 소켓을 특정 네트워크 인터페이스와 포트 번호에 연결하는데 사용됩니다.
# HOST는 hostname, ip address, 빈 문자열 ""이 될 수 있습니다.
# 빈 문자열이면 모든 네트워크 인터페이스로부터의 접속을 허용합니다.
# PORT는 1-65535 사이의 숫자를 사용할 수 있습니다.
#server_socket.bind((HOST, PORT))
server_socket.bind(("", PORT))

# 연결 리스닝(동시 접속) 수 설정
server_socket.listen(2)

print('클라이언트 연결 대기')

# 연결 수락(클라이언트 (소켓, 주소 정보) 반환)
client_socket, address = server_socket.accept()
print('클라이언트 ip 주소 :', address[0])

# 수신한 데이터를 넣을 버퍼(바이트 객체)
data_buffer = b""

# calcsize : 데이터의 크기(byte)
# - L : 부호없는 긴 정수(unsigned long) 4 bytes
data_size = struct.calcsize("L")

while True:
    # 설정한 데이터의 크기보다 버퍼에 저장된 데이터의 크기가 작은 경우
    while len(data_buffer) < data_size:
        # 데이터 수신
        data_buffer += client_socket.recv(4096)

    # 버퍼의 저장된 데이터 분할
    packed_data_size = data_buffer[:data_size]
    data_buffer = data_buffer[data_size:]

    # struct.unpack : 변환된 바이트 객체를 원래의 데이터로 반환
    # - > : 빅 엔디안(big endian)
    #   - 엔디안(endian) : 컴퓨터의 메모리와 같은 1차원의 공간에 여러 개의 연속된 대상을 배열하는 방법
    #   - 빅 엔디안(big endian) : 최상위 바이트부터 차례대로 저장
    # - L : 부호없는 긴 정수(unsigned long) 4 bytes
    frame_size = struct.unpack(">L", packed_data_size)[0]

    # 프레임 데이터의 크기보다 버퍼에 저장된 데이터의 크기가 작은 경우
    while len(data_buffer) < frame_size:
        # 데이터 수신
        data_buffer += client_socket.recv(4096)

    # 프레임 데이터 분할
    frame_data = data_buffer[:frame_size]
    data_buffer = data_buffer[frame_size:]

    print("수신 프레임 크기 : {} bytes".format(frame_size))

    # loads : 직렬화된 데이터를 역직렬화
    # - 역직렬화(de-serialization) : 직렬화된 파일이나 바이트 객체를 원래의 데이터로 복원하는 것
    frame = pickle.loads(frame_data)

    # imdecode : 이미지(프레임) 디코딩
    # 1) 인코딩된 이미지 배열
    # 2) 이미지 파일을 읽을 때의 옵션
    #    - IMREAD_COLOR : 이미지를 COLOR로 읽음
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

    # 프레임 출력
    cv2.imshow('Frame', frame)

    # 'q' 키를 입력하면 종료
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

# 소켓 닫기
client_socket.close()
server_socket.close()
print('연결 종료')

# 모든 창 닫기
cv2.destroyAllWindows()