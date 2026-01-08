#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSlock;
use TMSselitem;

#require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

require "../shift/shiftreport.pm";

my $menu_color = '#00A77E';
my $body_color = '#DCEFE7';

my $html = new CGI;

my %operator = ();
my @p = $html->param('operator');
if( $#p < 0 ){
  require '../common/http_header.pm';
  print &TMScommon::no_data_page( $menu_color, $body_color );
  exit;
}
foreach(@p){ $operator{$_} = 1; }

my $period = $html->param('period');
my @day    = $html->param('day');
@day = sort @day;

my @file = ();
my @index = ();
&TMScommon::get_operator_file_list( $period, \@day, \@file, \@index );	# @file:  期間(@day)にマッチするファイル名
									# @index: 期間(@day)の表示用文字列

my $update_lock = '../../tmsdata/update.lock';
my $other_user;
if( &TMSlock::check_lockfile($update_lock,$ENV{REMOTE_ADDR},\$other_user) ){	# データ更新中は使用不可
  require '../common/http_header.pm';
  print &TMSlock::data_updating_page( $other_user );
  exit;
}

# 各ファイル名の取得
my $xlsfile = "../xlsfile/$lang/shiftreport.xls";

my $datafile = &TMScommon::get_xlsdata_file_name("shiftreport","csv");

my $infofile = "shiftreport.tmshlp";


# ＣＳＶファイルの出力
my @val_item2     = &TMSselitem::get_value_of_item2();
my @val_item      = &TMSselitem::get_value_of_item();
my @val_item3     = &TMSselitem::get_value_of_item3();
my @val_detail    = &TMSselitem::get_value_of_detail();
my @val_color     = &TMSselitem::get_value_of_color();
my $val_beam_type = &TMSselitem::get_value_of_beam_type();
my $val_unit      = &TMSselitem::get_value_of_unit();

my @ttl_item2  = &TMSselitem::get_title_of_item2();
my @ttl_item   = &TMSselitem::get_title_of_item();
my @ttl_item3  = &TMSselitem::get_title_of_item3();
my @ttl_detail = &TMSselitem::get_title_of_detail();
my @ttl_color  = &TMSselitem::get_title_of_color();
my $ttl_unit   = &TMSselitem::get_title_of_unit();

my $jat_ari = &TMSselitem::is_jat_ari(),
my $lwt_ari = &TMSselitem::is_lwt_ari(),

my $jat_lwt_ari = (1==0); # False
if( ($jat_ari == 1) and ($lwt_ari == 1) ){ $jat_lwt_ari = (1==1); } # True


open(OUT, "> $datafile" );

my $now_date = &TMScommon::get_now_date();

print OUT	"( $now_date )\n".
		"$index[0] -> $index[$#index]\n".
		"\n";

print OUT &make_shiftreport_title( 'operator',
				   $period,
				   'loom',
				   $jat_ari, $lwt_ari,
				   $val_beam_type,
				   $ttl_unit,
				   \@val_item2,  \@ttl_item2,
				   \@val_item,   \@ttl_item,
				   \@val_item3,  \@ttl_item3,
				   \@val_detail, \@ttl_detail,
				   \@val_color,  \@ttl_color  );

my $dcount = 0;
for( my $i=0; $i<=$#file; $i++ ){
  my $f = $file[$i];
  open(IN,"< $f");
  while(<IN>){
    my $line = $_;
    if( $line =~ m/,ope_name ([^,]+)/ ){
      if( exists($operator{$1}) ){

        $dcount++;
        print OUT &make_shiftreport_data( 'operator',
					  $index[$i],
					  'loom',
					  \$line,
					  $jat_lwt_ari,
					  $val_beam_type,
					  $val_unit,
					  \@val_item2,
					  \@val_item,
					  \@val_item3,
					  \@val_detail,
					  \@val_color );
      }
    }
  }
  close(IN);
}
close(OUT);


if( $dcount == 0 ){
  require '../common/http_header.pm';
  print &TMScommon::no_data_page( $menu_color, $body_color );
}
else{
  # TmsHelper.exe 用情報データ出力
  &TMScommon::http_header_tmsinf($infofile);

  print "method POPUP_EXCEL\n";
  print "version 1.0\n";

  print "xlsfile ". &TMScommon::get_fullpath_url($xlsfile). "\n";

  if( $ENV{REMOTE_ADDR} eq '127.0.0.1' ){  # ローカルの場合（データ読み込み高速化の為）
    print "csvfile1 ". &TMScommon::get_fullpath_file($datafile). "\n";
  }else{  # リモートの場合
    print "csvfile1 ". &TMScommon::get_fullpath_url($datafile). "\n";
  }

  #print "macro start_make_all\n";
}

