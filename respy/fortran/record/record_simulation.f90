!******************************************************************************
!******************************************************************************
MODULE recording_simulation

  !/*	external modules	*/

    USE shared_constants

  !/*	setup	*/

    IMPLICIT NONE

    PRIVATE

    PUBLIC :: record_simulation

    !/* explicit interface   */

    INTERFACE record_simulation

        MODULE PROCEDURE record_simulation_progress, record_simulation_start, record_simulation_stop

    END INTERFACE

CONTAINS
!******************************************************************************
!******************************************************************************
SUBROUTINE record_simulation_start(num_agents_sim, seed_sim)

    !/* external objects        */

    INTEGER(our_int), INTENT(IN)    :: num_agents_sim
    INTEGER(our_int), INTENT(IN)    :: seed_sim

!------------------------------------------------------------------------------
! Algorithm
!------------------------------------------------------------------------------

    100 FORMAT(2x,A32,1x,i8,1x,A16,1x,i8)

    OPEN(UNIT=99, FILE='sim.respy.log', ACTION='WRITE')

        WRITE(99, 100) 'Starting simulation of model for', num_agents_sim, 'agents with seed', seed_sim
        WRITE(99, *)

    CLOSE(99)

END SUBROUTINE
!******************************************************************************
!******************************************************************************
SUBROUTINE record_simulation_stop()

!------------------------------------------------------------------------------
! Algorithm
!------------------------------------------------------------------------------

    OPEN(UNIT=99, FILE='sim.respy.log', ACCESS='APPEND', ACTION='WRITE')

        WRITE(99, *) ' ... finished'
        WRITE(99, *)

    CLOSE(99)

END SUBROUTINE
!******************************************************************************
!******************************************************************************
SUBROUTINE record_simulation_progress(i)

    !/* external objects        */

    INTEGER(our_int), INTENT(IN)    :: i

!------------------------------------------------------------------------------
! Algorithm
!------------------------------------------------------------------------------

    IF ((i .NE. zero_int) .AND. (MOD(i, 100) == zero_dble)) THEN

        100 FORMAT(A16,i10,A7)

        OPEN(UNIT=99, FILE='sim.respy.log', ACCESS='APPEND', ACTION='WRITE')

            WRITE(99, 100) ' ... simulated ', i, ' agents'
            WRITE(99, *)

        CLOSE(99)

    ELSE

        RETURN

    END IF

END SUBROUTINE
!******************************************************************************
!******************************************************************************
END MODULE
