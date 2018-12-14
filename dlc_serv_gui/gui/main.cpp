#include "dlcgui.h"
#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    dlcgui w;
    w.show();

    return a.exec();
}
