/* This file was generated by the Hex-Rays decompiler version 8.2.0.221215.
   Copyright (c) 2007-2021 Hex-Rays <info@hex-rays.com>

   Detected compiler: GNU C++
*/

#include <defs.h>


//-------------------------------------------------------------------------
// Function declarations

__int64 (**init_proc())(void);
__int64 __fastcall sub_400670(); // weak
// void free(void *ptr);
// int puts(const char *s);
// void setbuf(FILE *stream, char *buf);
// int printf(const char *format, ...);
// char *fgets(char *s, int n, FILE *stream);
// void *malloc(size_t size);
// FILE *fopen(const char *filename, const char *modes);
// __int64 __isoc99_scanf(const char *, ...); weak
// char *strcat(char *dest, const char *src);
void __fastcall __noreturn start(__int64 a1, __int64 a2, void (*a3)(void));
FILE **deregister_tm_clones();
__int64 register_tm_clones();
FILE **_do_global_dtors_aux();
__int64 frame_dummy();
int __cdecl main(int argc, const char **argv, const char **envp);
void _libc_csu_fini(void); // idb
void term_proc();
// int __fastcall _libc_start_main(int (__fastcall *main)(int, char **, char **), int argc, char **ubp_av, void (*init)(void), void (*fini)(void), void (*rtld_fini)(void), void *stack_end);
// __int64 _gmon_start__(void); weak

//-------------------------------------------------------------------------
// Data declarations

_UNKNOWN _libc_csu_init;
__int64 (__fastcall *_frame_dummy_init_array_entry)() = &frame_dummy; // weak
__int64 (__fastcall *_do_global_dtors_aux_fini_array_entry)() = &_do_global_dtors_aux; // weak
__int64 (*qword_601010)(void) = NULL; // weak
FILE *_bss_start; // idb
char completed_7698; // weak


//----- (0000000000400650) ----------------------------------------------------
__int64 (**init_proc())(void)
{
  __int64 (**result)(void); // rax

  result = &_gmon_start__;
  if ( &_gmon_start__ )
    return (__int64 (**)(void))_gmon_start__();
  return result;
}
// 6010E8: using guessed type __int64 _gmon_start__(void);

//----- (0000000000400670) ----------------------------------------------------
__int64 sub_400670()
{
  return qword_601010();
}
// 400670: using guessed type __int64 __fastcall sub_400670();
// 601010: using guessed type __int64 (*qword_601010)(void);

//----- (0000000000400720) ----------------------------------------------------
// positive sp value has been detected, the output may be wrong!
void __fastcall __noreturn start(__int64 a1, __int64 a2, void (*a3)(void))
{
  __int64 v3; // rax
  int v4; // esi
  __int64 v5; // [rsp-8h] [rbp-8h] BYREF
  char *retaddr; // [rsp+0h] [rbp+0h] BYREF

  v4 = v5;
  v5 = v3;
  _libc_start_main(
    (int (__fastcall *)(int, char **, char **))main,
    v4,
    &retaddr,
    (void (*)(void))_libc_csu_init,
    _libc_csu_fini,
    a3,
    &v5);
  __halt();
}
// 400726: positive sp value 8 has been found
// 40072D: variable 'v3' is possibly undefined

//----- (0000000000400760) ----------------------------------------------------
FILE **deregister_tm_clones()
{
  return &_bss_start;
}

//----- (0000000000400790) ----------------------------------------------------
__int64 register_tm_clones()
{
  return 0LL;
}

//----- (00000000004007D0) ----------------------------------------------------
FILE **_do_global_dtors_aux()
{
  FILE **result; // rax

  if ( !completed_7698 )
  {
    result = deregister_tm_clones();
    completed_7698 = 1;
  }
  return result;
}
// 601080: using guessed type char completed_7698;

//----- (0000000000400800) ----------------------------------------------------
__int64 frame_dummy()
{
  return register_tm_clones();
}

//----- (0000000000400807) ----------------------------------------------------
int __cdecl main(int argc, const char **argv, const char **envp)
{
  char *v3; // rax
  char v5; // [rsp+1Fh] [rbp-A1h] BYREF
  int v6; // [rsp+20h] [rbp-A0h] BYREF
  int i; // [rsp+24h] [rbp-9Ch]
  char *v8; // [rsp+28h] [rbp-98h]
  char *dest; // [rsp+30h] [rbp-90h]
  FILE *stream; // [rsp+38h] [rbp-88h]
  char *v11; // [rsp+40h] [rbp-80h]
  const char *v12; // [rsp+48h] [rbp-78h]
  char src[32]; // [rsp+50h] [rbp-70h] BYREF
  char s[72]; // [rsp+70h] [rbp-50h] BYREF
  unsigned __int64 v15; // [rsp+B8h] [rbp-8h]

  v15 = __readfsqword(0x28u);
  setbuf(_bss_start, 0LL);
  stream = fopen("flag.txt", "r");
  fgets(s, 64, stream);
  strcpy(src, "this is a random string.");
  v8 = 0LL;
  for ( i = 0; i <= 6; ++i )
  {
    dest = (char *)malloc(0x80uLL);
    if ( !v8 )
      v8 = dest;
    v3 = dest;
    *(_QWORD *)dest = 0x73746172676E6F43LL;
    strcpy(v3 + 8, "! Your flag is: ");
    strcat(dest, s);
  }
  v11 = (char *)malloc(0x80uLL);
  strcpy(v11, "Sorry! This won't help you: ");
  strcat(v11, src);
  free(dest);
  free(v11);
  v6 = 0;
  v5 = 0;
  puts("You may edit one byte in the program.");
  printf("Address: ");
  __isoc99_scanf("%d", &v6);
  printf("Value: ");
  __isoc99_scanf(" %c", &v5);
  v8[v6] = v5;
  v12 = (const char *)malloc(0x80uLL);
  puts(v12 + 16);
  return 0;
}
// 400700: using guessed type __int64 __isoc99_scanf(const char *, ...);

//----- (0000000000400A80) ----------------------------------------------------
void __fastcall _libc_csu_init(unsigned int a1, __int64 a2, __int64 a3)
{
  signed __int64 v3; // rbp
  __int64 i; // rbx

  v3 = &_do_global_dtors_aux_fini_array_entry - &_frame_dummy_init_array_entry;
  init_proc();
  if ( v3 )
  {
    for ( i = 0LL; i != v3; ++i )
      (*(&_frame_dummy_init_array_entry + i))();
  }
}
// 600E00: using guessed type __int64 (__fastcall *_frame_dummy_init_array_entry)();
// 600E08: using guessed type __int64 (__fastcall *_do_global_dtors_aux_fini_array_entry)();

//----- (0000000000400AF4) ----------------------------------------------------
void term_proc()
{
  ;
}

// nfuncs=34 queued=10 decompiled=10 lumina nreq=0 worse=0 better=0
// ALL OK, 10 function(s) have been successfully decompiled
