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

my $str_OTHER_LIST_SETTING	= &TMSstr::get_str( 'OTHER_LIST_SETTING'	);

my $str_UPDATE_SETTING		= &TMSstr::get_str( 'UPDATE_SETTING'	);
my $str_UPDATE_OK		= &TMSstr::get_str( 'UPDATE_OK'		);

my $str_LOOM_NAME		= &TMSstr::get_str( "LOOM_NAME"		);

my $str_PAGE			= &TMSstr::get_str( 'PAGE'		);

my $str_FORECAST_EFFICIENCY	= &TMSstr::get_str( 'FORECAST_EFFICIENCY'	);
my $str_CLOTH_LENGTH_CORRECTION	= &TMSstr::get_str( 'CLOTH_LENGTH_CORRECTION'	);


my $str_SETTING_RESULT		= &TMSstr::get_str( "SETTING_RESULT"	);
my $str_SETTING_SUCCEED		= &TMSstr::get_str( "SETTING_SUCCEED"	);
my $str_MENU			= &TMSstr::get_str( "MENU"		);
my $str_BACK			= &TMSstr::get_str( "BACK"		);

################################################################

## １ページの最大表示台数
use constant LOOM_DISP_MAX => 20;

my $html = new CGI;

my @loom_set;
my $tmp_file;


## 初めての表示（スキャナー設定ファイルから読み込み）
if( ! defined($html->param('tmp_file')) ){

  # スキャナーの設定ファイルから、必要な設定を読み出し
  @loom_set = &TMSscanner::get_loom_setting( "mac_name",
                                             "forecast_effic",
                                             "cloth_correction" );

  # 機台名が未設定の場合は、機台IDで表示
  foreach(@loom_set){
    if( length($$_[1]) == 0 ){ $$_[1] = $$_[0]; }
  }
  ## 機台名、機台ID順にソート
  @loom_set = sort { "$$a[1] $$a[0]" cmp "$$b[1] $$b[0]" } @loom_set;

  # 一時ファイル名を取得
  $tmp_file = &TMScommon::get_tmp_file_name("other");

}
## CGI パラメータから読み込み
else{

  # 設定前の値を一時ファイルから読み出し
  $tmp_file = $html->param('tmp_file');
  @loom_set = &TMSscanner::load_tmp_file($tmp_file);

  # 今回設定された値を読み出し
  my @set_mac_id           = $html->param('mac_id');
  my @set_forecast_effic   = $html->param('forecast_effic');
  my @set_cloth_correction = $html->param('cloth_correction');

  # 設定を上書きする
  foreach my $r_data (@loom_set){
    my $mac_id = $$r_data[0];
    for( my $i=0; $i<=$#set_mac_id; $i++ ){
      if( $mac_id eq $set_mac_id[$i] ){

        my $forecast_effic   = int($set_forecast_effic[$i]);
        my $cloth_correction = sprintf("%.1f",$set_cloth_correction[$i]);

        @$r_data = ( $$r_data[0],    # mac_id   は更新しない
                     $$r_data[1],    # mac_name は更新しない
                     $forecast_effic,
                     $cloth_correction );
        last;
      }
    }
  }

  #### 設定完了時 ####
  if( defined($html->param('submit')) ){

    &TMSscanner::update_loom_setting( \@loom_set,
                                      "",               # mac_name は更新しない
                                      "forecast_effic",
                                      "cloth_correction" );

    &disp_result_html();
    exit;
  }

}

## 一時ファイルに保存
&TMSscanner::save_tmp_file( $tmp_file, \@loom_set );


## 表示するページの判断
my $page_max = ($#loom_set + 1) / LOOM_DISP_MAX;
if( $page_max > int($page_max) ){ $page_max = int($page_max) + 1; }

my $page = 1;
for( my $n=1; $n<=$page_max; $n++ ){
  if( defined($html->param("page$n")) ){
    $page = $n;
    last;
  }
}

## 表示対象のデータ範囲
my $disp_start = LOOM_DISP_MAX * ($page -1);
my $disp_end   = LOOM_DISP_MAX * $page;
if( $disp_end > ($#loom_set +1) ){ $disp_end = ($#loom_set +1); }

&disp_input_html();
exit;


##########################################################################

sub disp_input_html
{
my $tbl_width = 630;

my $title = $str_OTHER_LIST_SETTING;
my $cgifile = 'otherset.cgi';
my $menu_color = '#fdb913';
my $body_color = '#fff2dd';
my $submit_button = $str_UPDATE_SETTING;


print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"<script language=JavaScript>\n".
	"<!--\n";

print &TMSjavascript::checkName();
print &TMSjavascript::checkNumber();

print	"  chkSubmit_flg = false;\n".
	"  function enableChkSubmit() {\n".
	"    chkSubmit_flg = true;\n".
	"  }\n".
	"  function checkSubmit(aForm) {\n".
	"    for( i=0; i<".($disp_end - $disp_start)."; i++ ){\n".
	"      if( ! checkNumber(aForm.forecast_effic[i], 10, 100) ){ return false; }\n".
	"      if( ! checkNumber(aForm.cloth_correction[i], 80, 120) ){ return false; }\n".
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

#### ページ切替ボタン ####
use constant PAGE_BUTTON_COLUMN_MAX => 5;

if( $page_max > 1 ){
  print	"<table cellpadding=2 cellspacing=2>\n";

  my $col_max;
  if( $page_max < PAGE_BUTTON_COLUMN_MAX ){ $col_max = $page_max; }
  else{ $col_max = PAGE_BUTTON_COLUMN_MAX; }

  my $n = 1;
  while( $n <= $page_max ){
    print "<tr align=center>\n";
    for (my $j=0; $j<$col_max; $j++ ){
      if( $n <= $page_max ){
        if( $n eq $page ){
          print "<td bgcolor=gray><input type=SUBMIT name=\"page$n\" value=\"$str_PAGE $n\" disabled></td>\n";
        }else{
          print "<td><input type=SUBMIT name=\"page$n\" value=\"$str_PAGE $n\"></td>\n";
        }
      }else{ print "<td></td>\n"; }
      ++$n;
    }
    print "</tr>\n";
  }
  print	"</table>\n";
}

#### 設定値タイトル ####
print	"<table border=1 frame=box width=$tbl_width cellpadding=1 cellspacing=1>\n".
	"<tr align=center bgcolor=$menu_color>\n".
	"<th nowrap><font color=white>$str_LOOM_NAME</font></th>\n".
	"<th nowrap><font color=white>$str_FORECAST_EFFICIENCY<BR>(%)</font></th>\n".
	"<th nowrap><font color=white>$str_CLOTH_LENGTH_CORRECTION<BR>(%)</font></th>\n".
	"</tr>\n";

#### 設定値の入力 ####
for( my $i=$disp_start; $i<$disp_end; $i++ ){

  my ($mac_id,
      $mac_name,
      $forecast_effic,
      $cloth_correction ) = @{$loom_set[$i]};

  # 機台名が未設定の場合は、機台IDを表示
  if( length($mac_name) == 0 ){ $mac_name = $mac_id; }

  print	"<tr align=center bgcolor=$body_color>\n".
	"<th><input type=hidden name=\"mac_id\" value=\"$mac_id\">$mac_name</th>\n".
	"<td nowrap><input type=text name=\"forecast_effic\" value=\"$forecast_effic\" size=4></td>\n".
	"<td nowrap><input type=text name=\"cloth_correction\" value=\"$cloth_correction\" size=6></td>\n".
	"</tr>\n";
}

#### submit ボタン ####
print	"<tr><td align=center bgcolor=$body_color colspan=9>\n".
	"<input type=SUBMIT name=\"submit\" value=\"$submit_button\" onClick=\"enableChkSubmit()\">\n".
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
my $menu_color = '#fdb913';
my $body_color = '#fff2dd';

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
	"<A HREF=\"otherset.cgi\"><IMG SRC=\"../image/back2_$lang.jpg\" width=85 height=27 alt=\"$str_BACK\" border=0></A>\n".
	"</NOBR>\n".
	"<BR><BR><BR><BR>\n".
	"</td></tr>\n".
	"</table><BR>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";
}

#####################################################################
