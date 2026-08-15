#include "phoenix_core_extension.h"

#include <gdextension_interface.h>
#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/core/defs.hpp>
#include <godot_cpp/godot.hpp>

using namespace godot;

static void initialize_phoenix_module(ModuleInitializationLevel level) {
	if (level == MODULE_INITIALIZATION_LEVEL_SCENE) {
		GDREGISTER_CLASS(PhoenixCore);
	}
}

static void uninitialize_phoenix_module(ModuleInitializationLevel level) {
	(void)level;
}

extern "C" GDExtensionBool GDE_EXPORT phoenix_redot_library_init(
		GDExtensionInterfaceGetProcAddress get_proc_address,
		GDExtensionClassLibraryPtr library,
		GDExtensionInitialization *initialization) {
	GDExtensionBinding::InitObject init(get_proc_address, library, initialization);
	init.register_initializer(initialize_phoenix_module);
	init.register_terminator(uninitialize_phoenix_module);
	init.set_minimum_library_initialization_level(MODULE_INITIALIZATION_LEVEL_SCENE);
	return init.init();
}
