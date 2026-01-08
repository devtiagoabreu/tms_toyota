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

require '../shift/efficiency.pm';

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
my $xlsfile = "../xlsfile/$lang/efficiency.xls";

my $datafile = &TMScommon::get_xlsdata_file_name("efficiency","csv");

my $infofile = "efficiency.tmshlp";


# ＣＳＶファイルの出力

open(OUT, "> $datafile" );

my $now_date = &TMScommon::get_now_date();

print OUT	"( $now_date )\n".
		"$index[0] -> $index[$#index]\n".
		"\n";

print OUT &make_efficiency_title( 'operator', $period,
                                  &TMSselitem::is_jat_ari(),
                                  &TMSselitem::is_lwt_ari() );


my $dcount = 0;
for( my $i=0; $i<=$#file; $i++ ){
  my $f = $file[$i];
  open(IN,"< $f");
  while(<IN>){
    my $line = $_;
    if( $line =~ m/,ope_name ([^,]+)/ ){
      if( exists($operator{$1}) ){

        $dcount++;
        print OUT &make_efficiency_data( 'operator', $index[$i], \$line );

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

