#!C:/Perl/bin/perl.exe -I../common
use strict;
use warnings;
use CGI;

# Carrega os módulos antigos TMS
use lib 'C:/Apache2/htdocs/tms/common';
require 'http_header.pm';
require 'TMSstr.pm';
require 'TMScommon.pm';
require 'TMSscanner.pm';

my $q = CGI->new;

# Sempre devolve JSON
print "Content-type: application/json\n\n";

###############################################################################
# AQUI VOCÊ COLOCA AS LEITURAS REAIS DO TMS
# Por enquanto deixei exemplos para rodar agora mesmo
###############################################################################
my @teares = (

    # MODELO — Substitua com os dados reais
    {
        id         => "00001",
        artigo     => 2220,
        status     => "em Operação",
        eficiencia => 90,
        rpm        => 958
    },
    {
        id         => "00002",
        artigo     => 2220,
        status     => "Trama",
        eficiencia => 82,
        rpm        => 945
    },
    {
        id         => "00003",
        artigo     => 2220,
        status     => "Desligada",
        eficiencia => 0,
        rpm        => 0
    },
    {
        id         => "00004",
        artigo     => 2220,
        status     => "Urdume",
        eficiencia => 70,
        rpm        => 930
    }

);

###############################################################################
# GERA JSON MANUALMENTE (compatível com Perl antigo)
###############################################################################

print "[\n";
my $first = 1;

foreach my $t (@teares) {

    print "," unless $first;
    $first = 0;

    # Geração do objeto JSON manual
    print "  {";
    print "\"id\":\"$t->{id}\",";
    print "\"artigo\":$t->{artigo},";
    print "\"status\":\"$t->{status}\",";
    print "\"eficiencia\":$t->{eficiencia},";
    print "\"rpm\":$t->{rpm}";
    print "}";
}

print "\n]\n";

exit;
