from scipy.optimize import fmin_powell
from scipy.optimize import fmin_bfgs

from respy.python.record.record_estimation import record_estimation_stop
from respy.python.record.record_estimation import record_estimation_final
from respy.python.shared.shared_auxiliary import dist_class_attributes
from respy.python.estimate.estimate_auxiliary import get_optim_paras
from respy.python.estimate.estimate_wrapper import OptimizationClass
from respy.python.shared.shared_auxiliary import dist_model_paras
from respy.python.shared.shared_constants import OPTIMIZERS_PYTH
from respy.python.simulate.simulate_python import pyth_simulate
from respy.python.estimate.estimate_wrapper import MaxfunError
from respy.python.shared.shared_auxiliary import create_draws
from respy.python.solve.solve_python import pyth_solve


def respy_interface(respy_obj, request, data_array=None):
    """ This function provides the interface to the PYTHOn functionality.
    """
    # Distribute class attributes
    model_paras, num_periods, num_agents_est, edu_start, is_debug, edu_max, \
        delta, num_draws_prob, seed_prob, num_draws_emax, seed_emax, \
        min_idx, is_myopic, is_interpolated, num_points_interp, maxfun, \
        optimizer_used, tau, paras_fixed, optimizer_options, seed_sim, \
        num_agents_sim, derivatives = dist_class_attributes( respy_obj,
            'model_paras', 'num_periods', 'num_agents_est', 'edu_start',
            'is_debug', 'edu_max', 'delta', 'num_draws_prob', 'seed_prob',
            'num_draws_emax', 'seed_emax', 'min_idx', 'is_myopic',
            'is_interpolated', 'num_points_interp', 'maxfun', 'optimizer_used',
            'tau', 'paras_fixed', 'optimizer_options', 'seed_sim',
            'num_agents_sim', 'derivatives')

    # Auxiliary objects
    dfunc_eps = derivatives[1]

    coeffs_a, coeffs_b, coeffs_edu, coeffs_home, shocks_cholesky = \
        dist_model_paras(model_paras, is_debug)

    if request == 'estimate':
        # Check that selected optimizer is in line with version of program.
        if maxfun > 0:
            assert optimizer_used in OPTIMIZERS_PYTH

        periods_draws_prob = create_draws(num_periods, num_draws_prob,
            seed_prob, is_debug)

        # Draw standard normal deviates for the solution and evaluation step.
        periods_draws_emax = create_draws(num_periods, num_draws_emax,
            seed_emax, is_debug)

        # Construct starting values
        x_free_start = get_optim_paras(coeffs_a, coeffs_b, coeffs_edu,
            coeffs_home, shocks_cholesky, 'free', paras_fixed, is_debug)

        x_all_start = get_optim_paras(coeffs_a, coeffs_b, coeffs_edu,
            coeffs_home, shocks_cholesky, 'all', paras_fixed, is_debug)

        # Collect arguments that are required for the criterion function. These
        # must be in the correct order already.
        args = (is_interpolated, num_draws_emax, num_periods, num_points_interp,
            is_myopic, edu_start, is_debug, edu_max, min_idx, delta,
            data_array, num_agents_est, num_draws_prob, tau,
            periods_draws_emax, periods_draws_prob)

        # Special case where just an evaluation at the starting values is
        # requested is accounted for. Note, that the relevant value of the
        # criterion function is always the one indicated by the class
        # attribute and not the value returned by the optimization algorithm.
        opt_obj = OptimizationClass()

        opt_obj.maxfun = maxfun
        opt_obj.paras_fixed = paras_fixed
        opt_obj.x_all_start = x_all_start

        if maxfun == 0:
            opt_obj.crit_func(x_free_start, *args)
            success = True
            message = 'Single evaluation of criterion function at starting ' \
                      'values.'

        elif optimizer_used == 'SCIPY-BFGS':

            bfgs_maxiter = optimizer_options['SCIPY-BFGS']['maxiter']
            bfgs_gtol = optimizer_options['SCIPY-BFGS']['gtol']

            try:
                rslt = fmin_bfgs(opt_obj.crit_func, x_free_start, args=args,
                    gtol=bfgs_gtol, epsilon=dfunc_eps, maxiter=bfgs_maxiter,
                    full_output=True, disp=False)

                success = (rslt[6] not in [1, 2])
                rslt = 'Optimization terminated successfully.'
                if rslt[5] == 1:
                    message = 'Maximum number of iterations exceeded.'
                elif rslt == 2:
                    message = 'Gradient and/or function calls not changing.'

            except MaxfunError:
                success = False
                message = 'Maximum number of iterations exceeded.'

        elif optimizer_used == 'SCIPY-POWELL':

            powell_maxiter = optimizer_options['SCIPY-POWELL']['maxiter']
            powell_maxfun = optimizer_options['SCIPY-POWELL']['maxfun']
            powell_xtol = optimizer_options['SCIPY-POWELL']['xtol']
            powell_ftol = optimizer_options['SCIPY-POWELL']['ftol']

            try:
                rslt = fmin_powell(opt_obj.crit_func, x_free_start, args,
                    powell_xtol, powell_ftol, powell_maxiter, powell_maxfun,
                    disp=0)

                success = (rslt[5] not in [1, 2])
                message = 'Optimization terminated successfully.'
                if rslt[5] == 1:
                    message = 'Maximum number of function evaluations.'
                elif rslt[5] == 2:
                    message = 'Maximum number of iterations.'

            except MaxfunError:
                success = False
                message = 'Maximum number of iterations exceeded.'

        record_estimation_final(opt_obj, success, message)
        record_estimation_stop()

    elif request == 'simulate':

        # Draw draws for the simulation.
        periods_draws_sims = create_draws(num_periods, num_agents_sim, seed_sim, is_debug)

        # Draw standard normal deviates for the solution and evaluation step.
        periods_draws_emax = create_draws(num_periods, num_draws_emax,
            seed_emax, is_debug)

        # Collect arguments to pass in different implementations of the
        # simulation.
        periods_payoffs_systematic, states_number_period, mapping_state_idx, \
            periods_emax, states_all = pyth_solve(coeffs_a, coeffs_b,
            coeffs_edu, coeffs_home, shocks_cholesky, is_interpolated,
            num_draws_emax, num_periods, num_points_interp, is_myopic,
            edu_start, is_debug, edu_max, min_idx, delta, periods_draws_emax)

        solution = (periods_payoffs_systematic, states_number_period,
            mapping_state_idx, periods_emax, states_all)

        data_array = pyth_simulate(periods_payoffs_systematic,
            mapping_state_idx, periods_emax, states_all, shocks_cholesky,
            num_periods, edu_start, edu_max, delta, num_agents_sim,
            periods_draws_sims, seed_sim)

        args = (solution, data_array)
    else:
        raise AssertionError

    return args


