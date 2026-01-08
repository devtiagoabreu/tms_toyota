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

my $str_STYLE_SETTING		= &TMSstr::get_str( 'STYLE_SETTING'	);

my $str_UPDATE_SETTING		= &TMSstr::get_str( 'UPDATE_SETTING'	);
my $str_UPDATE_OK		= &TMSstr::get_str( 'UPDATE_OK'		);

my $str_PAGE			= &TMSstr::get_str( 'PAGE'		);

my $str_STYLE_NAME		= &TMSstr::get_str( "STYLE_NAME"	);
my $str_DELETE			= &TMSstr::get_str( "DELETE"		);

my $str_DENSITY			= &TMSstr::get_str( 'DENSITY'		);
my $str_DOFF_LENGTH		= &TMSstr::get_str( 'DOFF_LENGTH'	);

my $str_SETTING_RESULT		= &TMSstr::get_str( "SETTING_RESULT"	);
my $str_SETTING_SUCCEED		= &TMSstr::get_str( "SETTING_SUCCEED"	);
my $str_MENU			= &TMSstr::get_str( "MENU"		);
my $str_BACK			= &TMSstr::get_str( "BACK"		);

my $str_ERROR			= &TMSstr::get_str( 'ERROR'			);
my $str_DUPLICATE_STYLE_NAME	= &TMSstr::get_str( 'DUPLICATE_STYLE_NAME'	);
my $str_BACK_TO_SETTING		= &TMSstr::get_str( 'BACK_TO_SETTING'		);

################################################################

my $html = new CGI;

my @style_mst;

my $length_unit;
my $density_unit;

my $tmp_file;


## 初めての表示（スキャナー設定ファイルから読み込み）
if( ! defined($html->param('tmp_file')) ){

  # スキャナー１からスタイルマスタを取得
  my @style_mst_txt = &TMSscanner::get_scanner_file( 1, "set/style_mst.txt" );

  # 現在、使用中のスタイルを取得
  my %use_style = ();
  my @loom_set = &TMSscanner::get_loom_setting( "style" );
  foreach(@loom_set){
    my $style = $$_[1];
    if( length($style) > 0 ){ $use_style{$style} = 1; }
  }

  my $i = 0;
  foreach(@style_mst_txt){
    my ($name,$density,$doff_len) = split(/\t/);
    my $on_use = 0;
    if( length($name) > 0 ){
      if( exists($use_style{$name}) ){
        delete $use_style{$name};  # スタイルが重複した場合に、２つ目移行を消せる様に。
        $on_use = 1;
      }
    }
    $style_mst[$i] = [$name,$on_use,$density,$doff_len];
    $i++;
  }
  for( ; $i<100; $i++ ){
    $style_mst[$i] = ["",0,"",""];
  }

  ## 単位設定読み出し
  my $beam_unit; ## ダミー
  &TMSscanner::get_unit_setting( \$length_unit, \$beam_unit, \$density_unit );

  # 一時ファイル名を取得
  $tmp_file = &TMScommon::get_tmp_file_name("style");

}
## CGI パラメータから読み込み
else{

  # 設定前の値を一時ファイルから読み出し
  $tmp_file = $html->param('tmp_file');
  @style_mst = &TMSscanner::load_tmp_file($tmp_file);

  # 今回設定された値を読み出し
  my @set_num       = $html->param('num');
  my @set_name      = $html->param('name');
  my @set_on_use    = $html->param('on_use');
  my @set_density   = $html->param('density');
  my @set_doff_len  = $html->param('doff_len');

  # 設定されたデータに上書き
  for( my $i=0; $i<=$#set_num; $i++ ){
    my $num = $set_num[$i];

    my $name = $set_name[$i];
    $name =~ s/^\s+//g;  # 先頭のスペース削除
    $name =~ s/\s+$//g;  # 末尾のスペース削除

    my $density  = $set_density[$i];
    my $doff_len = $set_doff_len[$i];
    if( length($name) > 0 ){
      $density  = sprintf("%.2f",$density);
      $doff_len = int($doff_len);
    }

    $style_mst[$num] = [$name, $set_on_use[$i], $density, $doff_len];
  }

  ## 単位設定読み出し
  $length_unit  = $html->param('length_unit');
  $density_unit = $html->param('density_unit');


  ## 設定完了時
  if( defined($html->param('submit')) ){

    #### スタイル名の重複チェック ####
    my @style_name = ();
    foreach(@style_mst){
      my $name = $$_[0];
      if( length($name) > 0 ){ push(@style_name,$name); }
    }
    @style_name = sort { $a cmp $b } @style_name;

    my @same_list = ();
    my $prev = "";
    foreach(@style_name){
      if( $prev eq $_ ){ push(@same_list,$_); }
      $prev = $_;
    }
    if( $#same_list >= 0 ){
      &TMSscanner::save_tmp_file( $tmp_file, \@style_mst );
      &disp_duplicate_error(\@same_list,$tmp_file);
      exit;
    }

    #### 設定をスキャナーに保存する ####

    ## まずは、品種名でソート
    @style_mst = sort { $$a[0] cmp $$b[0] } @style_mst;

    my @style_mst_txt = ();
    foreach( @style_mst ){
      my ($name,$on_use,$density,$doff_len) = @$_;

      if( length($name) > 0 ){
        push(@style_mst_txt, "$name\t$density\t$doff_len");
      }
    }

    # 設定ファイルをスキャナーに転送

    &TMSscanner::upload_scanner_file( "all",
                                      ["set/style_mst.txt","set/style_mst.update"],
                                      \@style_mst_txt,     ["update"] );

    &disp_result_html();
    exit;
  }
}

## 一時ファイルに保存
&TMSscanner::save_tmp_file( $tmp_file, \@style_mst );

my $page = 1;  # 次に表示するページ
if   ( defined($html->param('page2')) ){ $page = 2; }
elsif( defined($html->param('page3')) ){ $page = 3; }
elsif( defined($html->param('page4')) ){ $page = 4; }
elsif( defined($html->param('page5')) ){ $page = 5; }


&disp_input_html();
exit;

################################################################

sub disp_input_html
{

my $tbl_width = 630;

my $title = $str_STYLE_SETTING;
my $cgifile = 'styleset.cgi';
my $menu_color = '#ED1C24';
my $body_color = '#FDE1D4';
my $submit_button = $str_UPDATE_SETTING;

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"<script language=JavaScript>\n".
	"<!--\n".
	"  function del_style(num) {\n".
	#"    document.fminput.del[num].checked=false;\n".
	"    document.fminput.name[num].value=\"\";\n".
	"    document.fminput.density[num].value=\"\";\n".
	"    document.fminput.doff_len[num].value=\"\";\n".
	"  }\n\n".

	"  function dont_change(num) {\n".
	"    document.fminput.density[num].focus();\n".
	"  }\n\n";

print &TMSjavascript::checkName();
print &TMSjavascript::checkNumber();

print	"  chkSubmit_flg = false;\n".
	"  function enableChkSubmit() {\n".
	"    chkSubmit_flg = true;\n".
	"  }\n".
	"  function checkSubmit(aForm) {\n".
	"    for( i=0; i<20; i++ ){\n".
	"      res = checkName(aForm.name[i]);\n".
	"      if( res < 0 ){ return false; }\n".
	"      if( res > 0 ){\n".
	"        if( ! checkNumber(aForm.density[i], 3.5, 500) ){ return false; }\n".
	"        if( ! checkNumber(aForm.doff_len[i], 0, 99999.9) ){ return false; }\n".
	"      }\n".
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
print	"<input type=hidden name=\"tmp_file\" value=\"$tmp_file\">\n".
	"<input type=hidden name=\"length_unit\" value=\"$length_unit\">\n".
	"<input type=hidden name=\"density_unit\" value=\"$density_unit\">\n";

#### ページ切替ボタン ####
print	"<table cellpadding=3 cellspacing=3><tr align=center>\n";
for( my $n=1; $n<=5; $n++ ){
  if( $n == $page ){
    print "<td bgcolor=gray><input type=SUBMIT name=\"page$n\" value=\"$str_PAGE $n\" disabled></td>\n";
  }else{
    print "<td><input type=SUBMIT name=\"page$n\" value=\"$str_PAGE $n\"></td>\n";
  }
}
print	"</tr></table>\n";

#### 設定値タイトル ####
my @str_LENGTH_UNIT  = &TMSscanner::get_str_length_unit();
my @str_DENSITY_UNIT = &TMSscanner::get_str_density_unit();

print	"<table border=1 frame=box width=$tbl_width cellpadding=1 cellspacing=1>\n".
	"<tr align=center bgcolor=$menu_color>\n".
	"<th><font color=white>$str_STYLE_NAME</font></th>\n".
	"<th><font color=white>$str_DENSITY<BR>($str_DENSITY_UNIT[$density_unit])</font></th>\n".
	"<th><font color=white>$str_DOFF_LENGTH<BR>($str_LENGTH_UNIT[$length_unit])</font></th>\n".
	"</tr>\n";

my $disp_start = 20 * ($page -1);

#### 設定値の入力 ####
for( my $i=0; $i<20; $i++ ){

  my $num = $disp_start + $i;

  my ($name,$on_use,$density,$doff_len) = @{$style_mst[$num]};
  print	"<tr align=center bgcolor=$body_color>\n".
	"<td>\n".
	"<input type=hidden name=\"num\" value=\"$num\">\n".
	"<input type=hidden name=\"on_use\" value=\"$on_use\">\n";
  if( $on_use == 1 ){
    print "<input type=button name=\"del\" value=\"$str_DELETE\" disabled>&nbsp;&nbsp;\n".
	  "<input type=text name=\"name\" value=\"$name\" size=15 onFocus=\"dont_change($i)\"></td>\n";
  }else{
    print "<input type=button name=\"del\" value=\"$str_DELETE\" onClick=\"del_style($i)\">&nbsp;&nbsp;\n".
	  "<input type=text name=\"name\" value=\"$name\" size=15></td>\n";
  }
  print "</td>\n".
	"<td><input type=text name=\"density\" value=\"$density\" size=7></td>\n".
	"<td><input type=text name=\"doff_len\" value=\"$doff_len\" size=7></td>\n".
	"</tr>\n";
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
my $cgifile = 'styleset.cgi';
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

print	"<B><font color=red>$str_ERROR : $str_DUPLICATE_STYLE_NAME</font></B><BR><BR>\n";

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
	"<A HREF=\"styleset.cgi\"><IMG SRC=\"../image/back2_$lang.jpg\" width=85 height=27 alt=\"$str_BACK\" border=0></A>\n".
	"</NOBR>\n".
	"<BR><BR><BR><BR>\n".
	"</td></tr>\n".
	"</table><BR>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";
}

#####################################################################
