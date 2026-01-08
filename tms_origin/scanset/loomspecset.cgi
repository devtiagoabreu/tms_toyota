#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSjavascript;
use TMSscanner;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_LOOM_NAME_SPEC_SETTING	= &TMSstr::get_str( 'LOOM_NAME_SPEC_SETTING'	);

my $str_UPDATE_SETTING		= &TMSstr::get_str( 'UPDATE_SETTING'	);
my $str_UPDATE_OK		= &TMSstr::get_str( 'UPDATE_OK'		);

my $str_LOOM_NAME		= &TMSstr::get_str( "LOOM_NAME"		);
my $str_BEAM_TYPE		= &TMSstr::get_str( "BEAM_TYPE"		);
my $str_SINGLE_BEAM		= &TMSstr::get_str( "SINGLE_BEAM"	);
my $str_DOUBLE_BEAM		= &TMSstr::get_str( "DOUBLE_BEAM"	);

my $str_LOOM_ID			= &TMSstr::get_str( 'LOOM_ID'		);
my $str_SET_TO_ALL		= &TMSstr::get_str( 'SET_TO_ALL'	);

my $str_SETTING_RESULT		= &TMSstr::get_str( "SETTING_RESULT"	);
my $str_SETTING_SUCCEED		= &TMSstr::get_str( "SETTING_SUCCEED"	);
my $str_MENU			= &TMSstr::get_str( "MENU"		);
my $str_BACK			= &TMSstr::get_str( "BACK"		);

my $str_ERROR			= &TMSstr::get_str( 'ERROR'			);
my $str_DUPLICATE_MAC_NAME	= &TMSstr::get_str( 'DUPLICATE_MAC_NAME'	);
my $str_BACK_TO_SETTING		= &TMSstr::get_str( 'BACK_TO_SETTING'		);

################################################################

my $html = new CGI;

my @loom_set;
my $tmp_file;


## 初めての表示（スキャナー設定ファイルから読み込み）
if( ! defined($html->param('tmp_file')) ){

  # スキャナーの設定ファイルから、必要な設定を読み出し
  @loom_set = &TMSscanner::get_loom_setting( "mac_name",
                                             "ubeam_ari" );

  ## 機台ID順にソート
  @loom_set = sort { $$a[0] cmp $$b[0] } @loom_set;

  # 一時ファイル名を取得
  $tmp_file = &TMScommon::get_tmp_file_name("loomspec");

}
## CGI パラメータから読み込み
else{

  # 設定前の値を一時ファイルから読み出し
  $tmp_file = $html->param('tmp_file');
  @loom_set = &TMSscanner::load_tmp_file($tmp_file);

  # 今回設定された値を読み出し
  my @set_mac_id    = $html->param('mac_id');
  my @set_mac_name  = $html->param('mac_name');

  my @set_ubeam_ari = ();
  my $n = 0;
  while( defined($html->param("ubeam_ari$n")) ){
    $set_ubeam_ari[$n] = $html->param("ubeam_ari$n");
    ++$n;
  }

  # 設定を上書きする
  foreach my $r_data (@loom_set){
    my $mac_id = $$r_data[0];
    for( my $i=0; $i<=$#set_mac_id; $i++ ){
      if( $mac_id eq $set_mac_id[$i] ){
        @$r_data = ( $$r_data[0],   # 機台IDは、変更しない
                     $set_mac_name[$i],
                     $set_ubeam_ari[$i] );
        last;
      }
    }
  }

  #### 設定完了時 ####
  if( defined($html->param('submit')) ){

    ## 機台名の重複チェック ##
    my @mac_name = ();
    foreach(@loom_set){
      my $name = $$_[1];
      if( length($name) > 0 ){ push(@mac_name,$name); }
    }
    @mac_name = sort { $a cmp $b } @mac_name;

    my @same_list = ();
    my $prev = "";
    foreach(@mac_name){
      if( $prev eq $_ ){ push(@same_list,$_); }
      $prev = $_;
    }
    if( $#same_list >= 0 ){
      &TMSscanner::save_tmp_file( $tmp_file, \@loom_set );
      &disp_duplicate_error(\@same_list,$tmp_file);
      exit;
    }

    #### 設定をスキャナーに保存する ####

    &TMSscanner::update_loom_setting( \@loom_set,
                                      "mac_name",
                                      "ubeam_ari" );

    &disp_result_html();
    exit;
  }

}

## 一時ファイルに保存
&TMSscanner::save_tmp_file( $tmp_file, \@loom_set );

## 表示ループを決める
my $disp_loop;
if( defined($html->param("loop")) ){
  $disp_loop = $html->param("loop");
  $disp_loop =~ s/\.\*\*\*$//;   # S1-01.*** -> S1-01
}
else{
  ## 最初のデータのループを表示
  my $id = ${$loom_set[0]}[0];
  $disp_loop = substr($id,0,5);
}


## 表示するデータの抽出 ##
my @loop_list = ();
my @mac_id    = ();
my @mac_name  = ();
my @ubeam_ari = ();

foreach my $r_data (@loom_set){
  # 機台ID
  my $id = $$r_data[0];

  # ループ番号
  my $loop = substr($id,0,5);
  my $entry_flg = 0;
  foreach(@loop_list){
    if( $loop eq $_ ){ $entry_flg = 1; last; }
  }
  if( $entry_flg == 0 ){ push(@loop_list,$loop); }

  # 表示対象ループだけ、配列に入れる
  if( $disp_loop eq $loop ){
    push( @mac_id,    $id );
    push( @mac_name,  $$r_data[1] );
    push( @ubeam_ari, $$r_data[2] );
  }
}

## ページ数 ##
my $page_max = ($#loop_list + 1);

&disp_input_html();
exit;


################################################################

sub disp_input_html
{
my $tbl_width = 630;

my $title = $str_LOOM_NAME_SPEC_SETTING;
my $cgifile = 'loomspecset.cgi';
my $menu_color = '#ED1C24';
my $body_color = '#FDE1D4';
my $submit_button = $str_UPDATE_SETTING;

my $start = ($#loop_list +1) +2 +3;
my $end = $start + (4 * $#mac_id);

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"<script language=JavaScript>\n".
	"<!--\n".
	"  function sel_all_beam(offset) {\n".
        "    for( i=$start; i<=$end; i+=4 ){\n".
	"      document.fminput.elements[i+offset].checked = true;\n".
	"    }\n".
	"  }\n\n";

print &TMSjavascript::checkName();

print	"  chkSubmit_flg = false;\n".
	"  function enableChkSubmit() {\n".
	"    chkSubmit_flg = true;\n".
	"  }\n".
	"  function checkSubmit(aForm) {\n".
	"    for( i=0; i<$#mac_id; i++ ){\n".
	"      res = checkName(aForm.mac_name[i]);\n".
	"      if( res < 0 ){ return false; }\n".
	"    }\n".
	"    if( chkSubmit_flg ){\n".
	"      chkSubmit_flg = false;\n".
	"      return confirm(\"$str_UPDATE_OK\");\n".
	"    }\n".
	"    return true;\n".
	"  }\n".
	"//-->\n".
	"</script>\n".
	"</head>\n".
	"<body bgcolor=#C7C4E2><center>\n".
	&TMScommon::make_header('menu','dummy', $lang)."<BR>\n";

print	"<form name=\"fminput\" action=\"$cgifile\" method=POST onSubmit=\"return checkSubmit(this);\">\n".
	"<table width=$tbl_width><tr><th><font size=+2>$title</font></th></tr></table>\n";

### 隠し設定 ###
print	"<input type=hidden name=\"tmp_file\" value=\"$tmp_file\">\n";

#### ループ選択ボタン ####
use constant PAGE_BUTTON_COLUMN_MAX => 5;

if( $page_max > 1 ){
  print	"<table cellpadding=2 cellspacing=2>\n";

  my $col_max;
  if( $page_max < PAGE_BUTTON_COLUMN_MAX ){ $col_max = $page_max; }
  else{ $col_max = PAGE_BUTTON_COLUMN_MAX; }

  my $i = 0;
  while( $i < $page_max ){
    print "<tr align=center>\n";
    for (my $j=0; $j<$col_max; $j++ ){
      if( $i < $page_max ){
        my $loop = $loop_list[$i];
        if( $loop eq $disp_loop ){
          print "<td bgcolor=gray><input type=SUBMIT name=\"loop\" value=\"$loop.***\" disabled></td>\n";
        }else{
          print "<td><input type=SUBMIT name=\"loop\" value=\"$loop.***\"></td>\n";
        }
      }else{ print "<td></td>\n"; }
      ++$i;
    }
    print "</tr>\n";
  }
  print	"</table>\n";
}

#### 設定値タイトル ####
print	"<table border=1 frame=box width=$tbl_width cellpadding=1 cellspacing=1>\n".
	"<tr align=center bgcolor=$menu_color>\n".
	"<th rowspan=2><font color=white>$str_LOOM_ID</font></th>\n".
	"<th rowspan=2><font color=white>$str_LOOM_NAME</font></th>\n".
	"<th colspan=2><font color=white>$str_BEAM_TYPE</font></th>\n".
	"</tr>\n".
	"<tr align=center bgcolor=$menu_color>\n".
	"<th><font color=white>$str_SINGLE_BEAM</font><br>\n".
	"<input type=button value=\"$str_SET_TO_ALL\" onClick=\"sel_all_beam(0)\"></th>\n".
	"<th><font color=white>$str_DOUBLE_BEAM</font><br>\n".
	"<input type=button value=\"$str_SET_TO_ALL\" onClick=\"sel_all_beam(1)\"></th>\n".
	"</tr>\n";

#### 設定値の入力 ####
for( my $i=0; $i <= $#mac_id; $i++ ){
  if( $disp_loop eq substr($mac_id[$i],0,5) ){
    print "<tr align=center bgcolor=$body_color>\n".
	  "<th><input type=hidden name=\"mac_id\" value=\"$mac_id[$i]\">$mac_id[$i]</th>\n".
	  "<td><input type=text name=\"mac_name\" value=\"$mac_name[$i]\" size=15></td>\n";
    my @selected = ("","");
    if( $ubeam_ari[$i] == 0 ){ $selected[0] = "checked"; }
    else{                      $selected[1] = "checked"; }
    print "<td><input type=radio name=\"ubeam_ari$i\" value=\"0\" $selected[0]></td>\n";
    print "<td><input type=radio name=\"ubeam_ari$i\" value=\"1\" $selected[1]></td>\n";
    print "</tr>\n";
  }
}

#### submit ボタン ####
print	"<tr><td align=center bgcolor=$body_color colspan=5>\n".

	"<input type=SUBMIT name=\"submit\" value=\"$submit_button\" onClick=\"enableChkSubmit()\">\n".
	"</td></tr>\n".
	"</table>\n".
	"<BR></form>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";
}

#####################################################################

sub disp_duplicate_error
{
  my($r_same,$tmp_file) = @_;

my $tbl_width = 630;
my $title = $str_SETTING_RESULT;
my $cgifile = 'loomspecset.cgi';
my $menu_color = '#ED1C24';
my $body_color = '#FDE1D4';
my $submit_button = $str_BACK_TO_SETTING;

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"</head>\n".
	"<body bgcolor=#C7C4E2><center>\n".
	&TMScommon::make_header('menu','dummy', $lang)."<BR>";

print	"<form name=\"fminput\" action=\"$cgifile\" method=POST>\n".

	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
	"<tr align=center bgcolor=$menu_color>\n".
	"<th><font size=+2 color=white>$title</font></th>\n".
	"</tr>\n".
	"<tr align=center bgcolor=$body_color><td>\n".
	"<BR><BR>\n";

print	"<B><font color=red>$str_ERROR : $str_DUPLICATE_MAC_NAME</font></B><BR><BR>\n";

foreach(@$r_same){
  print "$_<BR>\n";
}

print	"<BR><BR>\n".
	"<input type=hidden name=\"tmp_file\" value=\"$tmp_file\">\n".
	"<input type=SUBMIT name=\"back\" value=\"$submit_button\">\n".
	"<BR><BR>\n".
	"</td></tr>\n".
	"</table>\n".
	"<BR></form>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";
}

#####################################################################

sub disp_result_html
{

my $tbl_width = 630;
my $title = $str_SETTING_RESULT;
my $menu_color = '#ED1C24';
my $body_color = '#FDE1D4';

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"</head>\n".
	"<body bgcolor=#C7C4E2><center>\n".
	&TMScommon::make_header('menu','dummy', $lang)."<BR>".

	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
	"<tr align=center bgcolor=$menu_color>\n".
	"<th><font size=+2 color=white>$title</font></th>\n".
	"</tr>\n".
	"<tr align=center bgcolor=$body_color><td>\n".
	"<BR><BR><BR>\n";

  print	"<font size=+2><B>$str_SETTING_SUCCEED</B></font>\n";

print	"<BR><BR><BR>\n".
	"<NOBR>\n".
	"<A HREF=\"../\"><IMG SRC=\"../image/menu2_$lang.jpg\" width=85 height=27 alt=\"$str_MENU\" border=0></A>\n".
	"<A HREF=\"loomspecset.cgi\"><IMG SRC=\"../image/back2_$lang.jpg\" width=85 height=27 alt=\"$str_BACK\" border=0></A>\n".
	"</NOBR>\n".
	"<BR><BR><BR><BR>\n".
	"</td></tr>\n".
	"</table><BR>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";
}

#####################################################################
