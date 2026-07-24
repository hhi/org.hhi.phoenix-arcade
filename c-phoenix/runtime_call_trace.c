#include <fcntl.h>
#include <stdatomic.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>

#define NO_INSTRUMENT __attribute__((no_instrument_function))
#define TRACE_EDGE_CAPACITY 8192

struct runtime_trace_header {
    char magic[8];
    uint64_t runtime_start;
    uint64_t dropped_edges;
    uint32_t edge_count;
    uint32_t reserved;
} __attribute__((packed));

struct runtime_trace_edge {
    uint64_t caller;
    uint64_t callee;
    uint64_t count;
} __attribute__((packed));

static struct runtime_trace_edge trace_edges[TRACE_EDGE_CAPACITY];
static atomic_flag trace_lock = ATOMIC_FLAG_INIT;
static atomic_bool trace_active;
static uint64_t trace_dropped_edges;
static int trace_fd = -1;

static uint64_t NO_INSTRUMENT hash_edge(uintptr_t caller, uintptr_t callee) {
    uint64_t hash = (uint64_t)caller;

    hash ^= (uint64_t)callee + 0x9e3779b97f4a7c15ULL + (hash << 6) + (hash >> 2);
    return hash;
}

static void NO_INSTRUMENT lock_trace(void) {
    while (atomic_flag_test_and_set_explicit(&trace_lock, memory_order_acquire)) {
    }
}

static void NO_INSTRUMENT unlock_trace(void) {
    atomic_flag_clear_explicit(&trace_lock, memory_order_release);
}

void NO_INSTRUMENT runtime_call_trace_start(const char *path) {
    memset(trace_edges, 0, sizeof(trace_edges));
    trace_dropped_edges = 0;
    trace_fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (trace_fd < 0) {
        return;
    }
    atomic_store_explicit(&trace_active, 1, memory_order_release);
}

void NO_INSTRUMENT runtime_call_trace_stop(void) {
    struct runtime_trace_header header = {
        {'C', 'P', 'H', 'X', 'C', 'G', '0', '1'},
        (uint64_t)(uintptr_t)&runtime_call_trace_start,
        0,
        0,
        0,
    };

    atomic_store_explicit(&trace_active, 0, memory_order_release);
    lock_trace();
    if (trace_fd >= 0) {
        header.dropped_edges = trace_dropped_edges;
        for (size_t i = 0; i < TRACE_EDGE_CAPACITY; i++) {
            if (trace_edges[i].count != 0) {
                header.edge_count++;
            }
        }
        (void)write(trace_fd, &header, sizeof(header));
        for (size_t i = 0; i < TRACE_EDGE_CAPACITY; i++) {
            if (trace_edges[i].count != 0) {
                (void)write(trace_fd, &trace_edges[i], sizeof(trace_edges[i]));
            }
        }
        (void)close(trace_fd);
        trace_fd = -1;
    }
    unlock_trace();
}

void NO_INSTRUMENT __cyg_profile_func_enter(void *callee, void *caller) {
    uintptr_t caller_address;
    uintptr_t callee_address;
    size_t slot;

    if (!atomic_load_explicit(&trace_active, memory_order_acquire)) {
        return;
    }

    caller_address = (uintptr_t)caller;
    callee_address = (uintptr_t)callee;
    lock_trace();
    if (!atomic_load_explicit(&trace_active, memory_order_relaxed)) {
        unlock_trace();
        return;
    }

    slot = (size_t)(hash_edge(caller_address, callee_address) % TRACE_EDGE_CAPACITY);
    for (size_t probe = 0; probe < TRACE_EDGE_CAPACITY; probe++) {
        struct runtime_trace_edge *edge = &trace_edges[slot];

        if (edge->count == 0) {
            edge->caller = caller_address;
            edge->callee = callee_address;
            edge->count = 1;
            unlock_trace();
            return;
        }
        if (edge->caller == caller_address && edge->callee == callee_address) {
            edge->count++;
            unlock_trace();
            return;
        }
        slot = (slot + 1) % TRACE_EDGE_CAPACITY;
    }

    trace_dropped_edges++;
    unlock_trace();
}

void NO_INSTRUMENT __cyg_profile_func_exit(void *callee, void *caller) {
    (void)callee;
    (void)caller;
}
