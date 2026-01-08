#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSlock;
use TMSrestruct;
use TMSipset;
use TMSDATAfinal;
use TMSDATAindex;

$| = 1;
require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_REPORT_DATA_RESTRUCTION	= &TMSstr::get_str( "REPORT_DATA_RESTRUCTION"	);
my $str_APPLY_CHANGE_TO_DATA	= &TMSstr::get_str( "APPLY_CHANGE_TO_DATA"	);
my $str_COMPLETED_ALL_PROPERLY	= &TMSstr::get_str( "COMPLETED_ALL_PROPERLY"	);

my $lockfile = '../../tmsdata/update.lock';
my $other_user;
if( &TMSlock::create_lockfile($lockfile,$ENV{REMOTE_ADDR},1,20,\$other_user) ){  # 同時使用を禁止（レベル１）
  print &TMSlock::data_updating_page( $other_user );
  exit;
}

my $html = new CGI;

# リダイレクトページの表示

my $title = $str_REPORT_DATA_RESTRUCTION;

#my $menu_color = '#0080EF';
my $body_color = '#D5E8F8';

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"</head>\n".
	"<body bgcolor=$body_color OnLoad=\"setTimeout('history.back()',2000)\">\n".
	"<pre>\n";

# ----------------------------------------------------------------------------
# データ再構築

print	"\n$str_APPLY_CHANGE_TO_DATA\n\n";

&TMSlock::update_lockfile($lockfile,$ENV{REMOTE_ADDR},1,600);  # ロックファイルを更新（レベル１）

&TMSDATAfinal::update_all_request();
&TMSDATAfinal::make_final( 1 );  # Phase 1

&TMSlock::update_lockfile($lockfile,$ENV{REMOTE_ADDR},1,600);  # ロックファイルを更新（レベル１）

&TMSDATAindex::make_index( 2 );  # Phase 2

# ----------------------------------------------------------------------------
# データ再構築要求ファイルを削除

&TMSrestruct::clr_restruction_request();

# ----------------------------------------------------------------------------

print	"\n**** $str_COMPLETED_ALL_PROPERLY ****\n".
	"</pre>\n".
	"</body></html>\n";

unlink($lockfile);	# ロックファイルを削除

