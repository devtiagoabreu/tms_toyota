#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use Win32API::File;
use Win32::File;

use TMSstr;
use TMScommon;
use TMSdeny;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_DATA_IMPORT_MEMCARD		= &TMSstr::get_str( "DATA_IMPORT_MEMCARD"	);
my $str_SELECT_ALL			= &TMSstr::get_str( "SELECT_ALL"		);
my $str_ENTER				= &TMSstr::get_str( "ENTER"			);
my $str_CURRENT_FOLDER			= &TMSstr::get_str( "CURRENT_FOLDER"		);
my $str_CANNOT_ACCESS_THIS_FOLDER	= &TMSstr::get_str( "CANNOT_ACCESS_THIS_FOLDER"	);
my $str_CANNOT_FIND_THIS_FOLDER		= &TMSstr::get_str( "CANNOT_FIND_THIS_FOLDER"	);
#my $str_MOVE_TO_THIS_FOLDER		= &TMSstr::get_str( "MOVE_TO_THIS_FOLDER"	);
#my $str_BACK_TO_PREV_FOLDER		= &TMSstr::get_str( "BACK_TO_PREV_FOLDER"	);
#my $str_SUB_FOLDER_LIST		= &TMSstr::get_str( "SUB_FOLDER_LIST"		);
my $str_FILE_LIST			= &TMSstr::get_str( "FILE_LIST"			);
#my $str_NO_SUB_FOLDERS			= &TMSstr::get_str( "NO_SUB_FOLDERS"		);
my $str_NO_FILES			= &TMSstr::get_str( "NO_FILES"			);
#my $str_MOVE_TO_SUB_FOLDER		= &TMSstr::get_str( "MOVE_TO_SUB_FOLDER"	);
#my $str_PARENT_FOLDER			= &TMSstr::get_str( "PARENT_FOLDER"		);
my $str_IMPORT_SELECTED_FILES		= &TMSstr::get_str( "IMPORT_SELECTED_FILES"	);

my $str_REGISTERED_FOLDER		= &TMSstr::get_str( "REGISTERED_FOLDER"	);
my $str_REGISTER			= &TMSstr::get_str( "REGISTER"		);
my $str_UNREGISTER			= &TMSstr::get_str( "UNREGISTER"	);


if( $ENV{REMOTE_ADDR} ne '127.0.0.1' ){
  print &TMSdeny::permission_deny_page();
  exit;
}

# 登録ファイルの読み出し
my @reg_datadir = ();
if( -f "datadir.txt" ){
  open( FILE, "< datadir.txt" );
  @reg_datadir = <FILE>;
  close(FILE);
  foreach(@reg_datadir){
    chomp; # 改行を取り除く
    s/^([a-z])/\u$1/;  # ドライブ名を大文字に変換(互換性の為)
  }
}

my $html = new CGI;

# 指定されたフォルダの読み出し
my $datadir = $html->param('datadir');

if( ! defined($datadir) ){
  if( $#reg_datadir >= 0 ){
    $datadir = $reg_datadir[0];
  }
  else{
    $datadir = "C:\\";	# デフォルト値
  }
}

if( $datadir =~ m/^[a-zA-Z]:$/ ){	# ドライブ名だけの場合は、\ を追加
  $datadir = "$datadir\\";
}

my $uc_datadir = uc $datadir;  # 大文字に変換


# フォルダの登録
if( defined($html->param('register')) ){
  my @tmplist = @reg_datadir;
  @reg_datadir = ($datadir);
  foreach(@tmplist){
    if( length($_) >= 3 ){
      my $ucd = uc $_;  # 大文字に変換して比較
      if( $ucd ne $uc_datadir ){
        push(@reg_datadir,$_);
      }
    }
  }
  if( $#reg_datadir > 9 ){ $#reg_datadir = 9; } # 最大10個まで

  # 登録ファイルを更新
  if( open(FILE,"> datadir.txt") ){
    foreach(@reg_datadir){ print FILE $_."\n"; }
    close(FILE);
  }
}

# フォルダの登録削除
if( defined($html->param('unregister')) ){
  my @tmplist = @reg_datadir;
  @reg_datadir = ();
  foreach(@tmplist){
    if( length($_) >= 3 ){
      my $ucd = uc $_;  # 大文字に変換して比較
      if( $ucd ne $uc_datadir ){
        push(@reg_datadir,$_);
      }
    }
  }

  # 登録ファイルを更新
  if( $#reg_datadir >= 0 ){
    if( open(FILE,"> datadir.txt") ){
      foreach(@reg_datadir){ print FILE $_."\n"; }
      close(FILE);
    }
  }else{
    unlink("datadir.txt");
  }

}

# 指定フォルダのファイル一覧の取得
my $filepath = $datadir;
$filepath =~ s/\\$//;		# 最後の \ を削除（フルパスのファイル名用）

my $dir_exist  = 0;
my $dir_access = 0;

my @file_list = ();
my @dir_list  = ();

if( -d $datadir ){
  $dir_exist = 1;

  if( opendir(DIR,$datadir) ){
    $dir_access = 1;
    my @tmp_list = readdir(DIR);
    closedir(DIR);
    foreach( @tmp_list){
      if( ($_ eq '.') or ($_ eq '..') ){ next; }

      # システム属性と隠し属性は除く(2008.3.8追加)
      my $attrbit = 0;
      if( 0 == Win32::File::GetAttributes("$filepath\\$_", $attrbit) ){ next; }
      if( $attrbit & (Win32::File::HIDDEN | Win32::File::SYSTEM) ){ next; }

      # フォルダとファイルに分ける
      #if( -d "$filepath\\$_" ){
      if( $attrbit & Win32::File::DIRECTORY ){ push(@dir_list, $_); }
      else{                                    push(@file_list,$_); }
    }
  }
}

# -------------- ここから画面表示 ------------------------

my $tbl_width = 720;
my $menu_color = '#FDB913';
my $body_color = '#FFF2DD';

my $mycgi   = 'mcdata.cgi';
my $cgifile = 'mcdata2.cgi';
my $title = $str_DATA_IMPORT_MEMCARD;
my $submit_button = $str_ENTER;

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"<script language=JavaScript>\n".
	"<!--\n".
	"  function sel_dir1() {\n".
	"    document.fminput1.submit();\n".
	"  }\n".
	"  function sel_dir2() {\n".
	"    document.fminput2.submit();\n".
	"  }\n".
	"  function sel_file() {\n".
	"    document.fminput.all_file.checked = false;\n".
	"  }\n".
	"  function sel_all_file() {\n".
	"    len = document.fminput.file.length;\n".
	"    val = document.fminput.all_file.checked;\n".
	"    for (i = 0; i < len; i++) {\n".
	"      document.fminput.file.options[i].selected = val;\n".
	"    }\n".
	"  }\n".
	"//-->\n".
	"</script>\n".
	"</head>\n".
	"<body bgcolor=#C7C4E2><center>\n".
	&TMScommon::make_header('menu','dummy', $lang)."<BR>\n".

	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
	"<tr align=center bgcolor=$menu_color>\n".
	"<th colspan=2><font size=+2 color=white>$title</font></th>\n".
	"</tr>\n";

# -------------- 上段の登録フォルダ ---------------------------------------

my $reg_flg = 0;
my $option_html = "";
foreach( @reg_datadir ){
  my $selected = "";
  my $ucd = uc $_;  # 大文字に変換して比較
  if( $ucd eq $uc_datadir ){ $selected = "selected"; $reg_flg = 1; }
  $option_html .= "<option value=\"$_\" $selected>$_</option>\n";
}

print	"<form name=\"fminput2\" action=\"$mycgi\" method=POST>\n".
	"<tr bgcolor=$body_color><td colspan=2 align=center>\n".
	"<B>$str_REGISTERED_FOLDER : </B>\n".
	"<select name=\"datadir\" onChange=\"sel_dir2();\">\n";
if( $reg_flg == 0 ){
  print	"<option value=\"\"></option>\n";
}
print	$option_html."</select>\n";

print	"</td></tr>\n".
	"</form>\n";

# -------------- 左側のフォルダ階層 ---------------------------------------

print	"<tr valign=top bgcolor=$body_color>\n".
	"<form name=\"fminput1\" action=\"$mycgi\" method=POST>\n".
	"<td align=center width=50%>\n".

	"<B>$str_CURRENT_FOLDER</B><BR>\n".
        "<table border=1 cellspacing=0 cellpadding=4 width=320 bgcolor=white>\n";

my $idnum = 1;  # id用番号

my @dir = split(/\\/,$filepath);

# 現在、有効なドライブ一覧を取得
my @drives = Win32API::File::getLogicalDrives();
foreach my $drv (@drives){

  # ドライブの種類
  my $dtype = Win32API::File::GetDriveType($drv);
  if(    $dtype == Win32API::File::DRIVE_REMOVABLE ){ $dtype = " (Removable)"; }
  elsif( $dtype == Win32API::File::DRIVE_CDROM     ){ $dtype = " (CD-ROM)";    }
  elsif( $dtype == Win32API::File::DRIVE_REMOTE    ){ $dtype = " (Network)";   }
  else{ $dtype = ""; }

  $drv =~ s/\\$//;

  print "<tr><td nowrap align=left>\n";

  if( $drv eq $dir[0] ){ # 現在のドライブ
    my $checked = "";
    my $b1 = "";
    my $b2 = "";
    my $path = $drv;

    # 階層表示
    for( my $i=0; $i<=$#dir; $i++ ){
      my $mark = "";
      my $type = "";
      if( $i >= 1 ){ $mark = "+"; $path .= "\\".$dir[$i]; $dtype = ""; }
      if( $i == $#dir ){ $checked = "checked"; $b1="<B>"; $b2="</B>"; }
      print "&nbsp; "x$i.$mark."<input type=radio name=\"datadir\" value=\"$path\" id=\"dir$idnum\" onClick=\"sel_dir1();\" $checked>".
            "<label for=\"dir$idnum\">$b1$dir[$i]$b2$dtype</label><BR>\n";
      ++$idnum;
    }
    # サブディレクトリ一覧
    foreach(@dir_list){
      print "&nbsp; "."&nbsp; "x($#dir+1)."<input type=radio name=\"datadir\" value=\"$path\\$_\" id=\"dir$idnum\" onClick=\"sel_dir1();\">".
            "<label for=\"dir$idnum\">$_</label><BR>\n";
      ++$idnum;
    }
  }else{ # 現在以外のドライブ
    print "<input type=radio name=\"datadir\" value=\"$drv\" id=\"dir$idnum\" onClick=\"sel_dir1();\">".
          "<label for=\"dir$idnum\">$drv$dtype</label><BR>\n";
    ++$idnum;
  }
  print "</td></tr>\n";
}
print	"</table><BR>\n".
	"<input type=SUBMIT name=\"register\" value=\"$str_REGISTER\"";
if( $dir_exist == 0 ){ print " disabled"; }
print	">\n".
	"<input type=SUBMIT name=\"unregister\" value=\"$str_UNREGISTER\"";
if( $reg_flg == 0 ){ print " disabled"; }
print	">\n".
	"</td>\n".
	"</form>\n";

# -------------- 右側のファイル一覧 ---------------------------------------

print	"<form name=\"fminput\" action=\"$cgifile\" method=POST>\n".
	"<td align=center valign=top bgcolor=$body_color>\n".
	"<B>$str_FILE_LIST</B><BR>\n";

# アクセス不可の場合
if( $dir_access == 0 ){
  print "<BR><BR><BR><BR><BR>\n".
        "<B><font color=red>";
  if( $dir_exist ){ print $str_CANNOT_ACCESS_THIS_FOLDER; }
  else{             print $str_CANNOT_FIND_THIS_FOLDER;   }
  print "</font></B>\n".
	"<BR><BR><BR><BR><BR><BR><BR><BR><BR>\n".
	"<BR><BR><BR><BR><BR><BR><BR><BR><BR>\n";
}

# ファイルが無い場合
elsif( $#file_list <= -1 ){
  print "<BR><BR><BR><BR><BR>\n".
	"<font color=blue>$str_NO_FILES</font>\n".
	"<BR><BR><BR><BR><BR><BR><BR><BR><BR>\n".
	"<BR><BR><BR><BR><BR><BR><BR><BR><BR>\n";
}

# ファイル一覧
else{
  print "<select name=\"file\" size=25 multiple onFocus=\"sel_file()\">\n";
  foreach( @file_list){ print "<option value=\"$filepath\\$_\">$_</option>\n"; }
  print "</select><br>\n".
	  "<input type=hidden name=\"datadir\" value=\"$datadir\">\n".
	  "<input type=CHECKBOX name=\"all_file\" OnClick=\"sel_all_file()\"><B>$str_SELECT_ALL</B><BR><BR>\n".
	  "<input type=SUBMIT name=\"submit\" value=\"$str_IMPORT_SELECTED_FILES\">\n";
}
print	"</td>\n".
	"</form>\n".
	"</tr>\n".
	"</table><BR>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";

