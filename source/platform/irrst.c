#include "irrst.h"
#include <stdint.h>

// Small, self-contained subset of libctru's svc/IPC contracts. The executable
// already ships with an exheader that grants ir:rst; no Ocarina Reframed
// runtime payload is used.
typedef u32 Handle;
typedef s32 Result;
typedef struct { u32 base_addr, size, perm, state; } MemInfo;
typedef struct { u32 flags; } PageInfo;

enum { MEMSTATE_FREE = 0, MEMPERM_READ = 1, MEMPERM_DONTCARE = 0x10000000 };

extern Result svcQueryMemory(MemInfo* info, PageInfo* page, u32 addr);
extern Result svcMapMemoryBlock(Handle memblock, u32 addr, u32 myPerm, u32 otherPerm);
extern Result svcCloseHandle(Handle handle);
extern Result svcConnectToPort(volatile Handle* out, const char* portName);
extern Result svcSendSyncRequest(Handle session);

static Handle sIrrstHandle;
static Handle sIrrstMemHandle;
static Handle sIrrstEvent;
static volatile u32* sIrrstShared;
static u32 sHeld;
static s16 sCstickX;
static s16 sCstickY;
static u8 sReady;

static inline u32* CommandBuffer(void) {
    void* tls;
    __asm__("mrc p15, 0, %0, c13, c0, 3" : "=r"(tls));
    return (u32*)((u8*)tls + 0x80);
}

static Result SrvRegisterClient(Handle srv) {
    u32* cmd = CommandBuffer();
    cmd[0] = 0x00010002;
    cmd[1] = 0x20; // current-process-id descriptor
    Result rc = svcSendSyncRequest(srv);
    return rc < 0 ? rc : (Result)cmd[1];
}

static Result SrvGetIrrst(Handle srv, Handle* out) {
    u32* cmd = CommandBuffer();
    cmd[0] = 0x00050100;
    cmd[1] = 0x723A7269; // "ir:r"
    cmd[2] = 0x00007473; // "st"
    cmd[3] = 6;
    cmd[4] = 0;
    Result rc = svcSendSyncRequest(srv);
    if (rc < 0) return rc;
    rc = (Result)cmd[1];
    if (rc >= 0 && out) *out = cmd[3];
    return rc;
}

static Result IrrstGetHandles(void) {
    u32* cmd = CommandBuffer();
    cmd[0] = 0x00010000;
    Result rc = svcSendSyncRequest(sIrrstHandle);
    if (rc < 0) return rc;
    rc = (Result)cmd[1];
    if (rc >= 0) {
        sIrrstMemHandle = cmd[3];
        sIrrstEvent = cmd[4];
    }
    return rc;
}

static Result IrrstInitialize(void) {
    u32* cmd = CommandBuffer();
    cmd[0] = 0x00020080;
    cmd[1] = 10;
    cmd[2] = 0;
    Result rc = svcSendSyncRequest(sIrrstHandle);
    return rc < 0 ? rc : (Result)cmd[1];
}

static u32 FindMapAddress(void) {
    u32 addr = 0x10000000;
    while (addr < 0x14000000) {
        MemInfo info;
        PageInfo page;
        if (svcQueryMemory(&info, &page, addr) < 0) return 0;
        if (info.state == MEMSTATE_FREE) {
            const u32 available = info.size - (addr - info.base_addr);
            if (available >= 0x1000) return addr;
        }
        const u32 next = info.base_addr + info.size;
        if (next <= addr) return 0;
        addr = next;
    }
    return 0;
}

u8 Irrst_Init(void) {
    if (sReady) return 1;

    Handle srv = 0;
    if (svcConnectToPort(&srv, "srv:") < 0) return 0;
    if (SrvRegisterClient(srv) < 0 || SrvGetIrrst(srv, &sIrrstHandle) < 0) {
        svcCloseHandle(srv);
        return 0;
    }
    svcCloseHandle(srv);

    if (IrrstGetHandles() < 0) return 0;
    // Some environments have already initialized ir:rst. Either result still
    // leaves the returned shared-memory handle authoritative.
    (void)IrrstInitialize();

    const u32 address = FindMapAddress();
    if (address == 0) return 0;
    if (svcMapMemoryBlock(sIrrstMemHandle, address, MEMPERM_READ,
                          MEMPERM_DONTCARE) < 0) return 0;

    sIrrstShared = (volatile u32*)address;
    sHeld = 0;
    sCstickX = 0;
    sCstickY = 0;
    sReady = 1;
    return 1;
}

static u8 Irrst_SectionStable(u32 id) {
    // Match libctru's ir:rst guard at the ring wrap boundary.  Entry 0 can be
    // observed while the service is rotating timestamps; treating that
    // half-written instant as a real zero/garbage sample is what made the
    // C-stick and ZL/ZR occasionally drop for a frame.
    if (id != 0) return 1;
    const int64_t tick0 = *(volatile int64_t*)&sIrrstShared[0];
    const int64_t tick1 = *(volatile int64_t*)&sIrrstShared[2];
    return tick0 != tick1 && tick0 >= 0 && tick1 >= 0;
}

void Irrst_Scan(void) {
    if (!sReady || !sIrrstShared) {
        sHeld = 0;
        sCstickX = 0;
        sCstickY = 0;
        return;
    }

    u32 id = sIrrstShared[4];
    if (id > 7) id = 7;
    if (!Irrst_SectionStable(id)) {
        // Preserve the last coherent sample instead of injecting a one-frame
        // false release / zero-stick reading.  The next frame will pick up
        // the completed ir:rst entry.
        return;
    }

    const u32 entry = 6 + id * 4;
    const u32 held = sIrrstShared[entry];

    // IRRST entry +0x0C packs signed C-stick X in the low halfword and Y in
    // the high halfword. Center is exactly zero; hardware range is roughly
    // -0x9C..0x9C. This is the same New-3DS input lane already used for ZL/ZR.
    const u32 packed = sIrrstShared[entry + 3];
    sHeld = held;
    sCstickX = (s16)(packed & 0xFFFFu);
    sCstickY = (s16)(packed >> 16);
}

u32 Irrst_KeysHeld(void) {
    return sReady ? sHeld : 0;
}

void Irrst_CstickRead(s16* x, s16* y) {
    if (x) *x = sReady ? sCstickX : 0;
    if (y) *y = sReady ? sCstickY : 0;
}
