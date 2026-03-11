#include "h/globals.h"

void init_lua( CHAR_DATA *ch ) { (void)ch; }
void init_lua( OBJ_DATA *obj ) { (void)obj; }
void init_lua( ROOM_INDEX_DATA *room ) { (void)room; }

lua_State *find_lua_function( CHAR_DATA *ch, string arg ) { (void)ch; (void)arg; return NULL; }
lua_State *find_lua_function( OBJ_DATA *ob, string arg ) { (void)ob; (void)arg; return NULL; }
lua_State *find_lua_function( ROOM_INDEX_DATA *rm, string arg ) { (void)rm; (void)arg; return NULL; }

void call_lua_function( lua_State *L, string str, const int nArgs ) { (void)L; (void)str; (void)nArgs; }
int RegisterLuaRoutines( lua_State *L ) { (void)L; return 0; }
int CallLuaWithTraceBack( lua_State *L, const int iArguments, const int iReturn ) { (void)L; (void)iArguments; (void)iReturn; return 0; }
void GetTracebackFunction( lua_State *L ) { (void)L; }

ROOM_INDEX_DATA *L_getroom( lua_State *L ) { (void)L; return NULL; }
CHAR_DATA *L_getchar( lua_State *L ) { (void)L; return NULL; }
int L_character_info( lua_State *L ) { (void)L; return 0; }
int L_obj_info( lua_State *L ) { (void)L; return 0; }
int L_room_info( lua_State *L ) { (void)L; return 0; }
int L_send_to_char( lua_State *L ) { (void)L; return 0; }
int L_recho( lua_State *L ) { (void)L; return 0; }

void call_lua( LUA_DATA *lua, string str, string arg ) { (void)lua; (void)str; (void)arg; }
void call_lua( CHAR_DATA *ch, string str, string arg ) { (void)ch; (void)str; (void)arg; }
void call_lua( OBJ_DATA *ob, string str, string arg ) { (void)ob; (void)str; (void)arg; }
void call_lua( ROOM_INDEX_DATA *rm, string str, string arg ) { (void)rm; (void)str; (void)arg; }

lua_State *luaL_newstate( void ) { return NULL; }
void lua_close( lua_State *L ) { (void)L; }
int luaL_loadfile( lua_State *L, const char *filename ) { (void)L; (void)filename; return 1; }
int lua_pcall( lua_State *L, int nargs, int nresults, int errfunc ) { (void)L; (void)nargs; (void)nresults; (void)errfunc; return 1; }
const char *lua_tolstring( lua_State *L, int idx, size_t *len )
{
   (void)L;
   (void)idx;
   if( len )
      *len = 12;
   return "lua disabled";
}
