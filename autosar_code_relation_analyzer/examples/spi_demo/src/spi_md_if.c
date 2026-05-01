#include "spi_md_if.h"

SpiIfStateType Spi_MD_If;
static int g_State = 0;

static void SpiIf_Helper(int *counter)
{
    (*counter)++;
}

FUNC(void, SPIIF_CODE) SpiIf_MainFunction(void)
{
    g_State = 1;
    if (g_State == 1) {
        Spi_MD_If.ready_flag = 1;
    }
    SpiIf_Helper(&g_State);
}
